"""Ariza shakli maydonlari, ularni tekshirish va ko'rsatish."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any

from aiogram.types import Message

from . import texts
from .config import now
from .db import Contest

MAX_PARTICIPANTS = 100


@dataclass(frozen=True)
class Field:
    key: str
    label: str  # tasdiqlash oynasi va Excel ustuni uchun
    prompt: str
    type: str = "text"  # text | date | choice | phone | list | video
    optional: bool = False
    max_len: int = 200
    free_prompt: str = ""  # choice: tanlov uchun ro'yxat berilmagan bo'lsa


FULL_NAME = Field(
    "full_name",
    "F.I.Sh.",
    "Ishtirokchining familiyasi, ismi va otasining ismini yozing:\n"
    "<i>Masalan: Karimova Madina Rustamovna</i>",
)
BIRTH_DATE = Field(
    "birth_date",
    "Tug'ilgan sana",
    "Tug'ilgan sanasini kun.oy.yil ko'rinishida yozing:\n<i>Masalan: 05.03.2012</i>",
    type="date",
)
TEAM_NAME = Field(
    "team_name",
    "Jamoa / ansambl nomi",
    "Jamoa yoki ansambl nomini yozing:\n<i>Masalan: «Navo» xalq cholg'ulari ansambli</i>",
)
PARTICIPANTS = Field(
    "participants",
    "Ishtirokchilar",
    "Har bir ishtirokchining familiyasi, ismi va otasining ismini <b>alohida qatorda</b> yozing:\n"
    "<i>Karimova Madina Rustamovna\nAliyev Jasur Akmalovich</i>",
    type="list",
    max_len=150,
)
INSTITUTION = Field(
    "institution",
    "Ta'lim muassasasi",
    "Tahsil olayotgan ta'lim muassasasini yozing (o'quvchi va talabalar uchun):\n"
    "<i>Masalan: Toshkent shahar 1-son bolalar musiqa va san'at maktabi</i>",
    optional=True,
    max_len=300,
)
DIRECTION = Field(
    "direction",
    "Yo'nalish",
    "Ishtirok etadigan yo'nalishni tanlang:",
    type="choice",
    free_prompt="Ishtirok etadigan yo'nalish nomini yozing:",
)
AGE_CATEGORY = Field(
    "age_category",
    "Yosh toifasi",
    "Ishtirok etadigan yosh toifasini tanlang:",
    type="choice",
    free_prompt="Ishtirok etadigan yosh toifasini yozing:",
)
PIECE = Field(
    "piece",
    "Asar nomi va muallifi",
    "Ijro etiladigan asar nomi va muallifini yozing:\n<i>Masalan: «Bahor valsi» — F. Shopen</i>",
    max_len=500,
)
TEACHER = Field("teacher", "O'qituvchi", "O'qituvchisining F.I.Sh.:", optional=True)
ACCOMPANIST = Field("accompanist", "Konsertmeyster", "Konsertmeysterining F.I.Sh.:", optional=True)
PARENTS = Field(
    "parents",
    "Ota-onasi",
    "Otasi va onasining F.I.Sh.:\n<i>Masalan: Karimov Rustam Aliyevich, Karimova Dilnoza Ahmedovna</i>",
    optional=True,
    max_len=300,
)
HEAD = Field(
    "head",
    "Muassasa rahbari",
    "Ta'lim muassasasi rahbarining F.I.Sh. (o'quvchi va talabalar uchun):",
    optional=True,
)
PHONE = Field(
    "phone",
    "Telefon",
    f"Ishtirokchining telefon raqami: «{texts.BTN_PHONE}» tugmasini bosing yoki qo'lda yozing.\n"
    "<i>Masalan: +998 90 123 45 67</i>",
    type="phone",
)
VIDEO = Field(
    "video",
    "Ijro videosi",
    "Ijro videosini yuboring: video faylni shu yerga tashlang yoki havolasini yozing "
    "(YouTube, Google Drive va h.k.).",
    type="video",
)

SOLO_FIELDS = (
    FULL_NAME, BIRTH_DATE, INSTITUTION, DIRECTION, AGE_CATEGORY, PIECE,
    TEACHER, PARENTS, ACCOMPANIST, HEAD, PHONE,
)
TEAM_FIELDS = (
    TEAM_NAME, PARTICIPANTS, INSTITUTION, DIRECTION, AGE_CATEGORY, PIECE,
    TEACHER, ACCOMPANIST, PARENTS, HEAD, PHONE,
)
ALL_FIELDS = {f.key: f for f in (*SOLO_FIELDS, *TEAM_FIELDS, VIDEO)}


def fields_for(kind: str, contest: Contest) -> tuple[Field, ...]:
    base = SOLO_FIELDS if kind == "solo" else TEAM_FIELDS
    return (*base, VIDEO) if contest.require_video else base


def options_for(field: Field, contest: Contest) -> list[str]:
    if field.key == "direction":
        return contest.directions
    if field.key == "age_category":
        return contest.age_categories
    return []


def prompt_for(field: Field, options: list[str]) -> str:
    if field.type == "choice" and not options:
        return field.free_prompt
    text = field.prompt
    if field.optional:
        text += texts.OPTIONAL_HINT
    return text


# --- tekshirish ---


class FormError(Exception):
    pass


def clean_text(text: str, max_len: int, min_len: int = 2) -> str:
    text = " ".join(text.split())
    if len(text) < min_len:
        raise FormError(texts.ERR_SHORT)
    if len(text) > max_len:
        raise FormError(texts.ERR_LONG.format(n=max_len))
    return text


def parse_date(text: str) -> date:
    m = re.fullmatch(r"\s*(\d{1,2})\s*[./\-,]\s*(\d{1,2})\s*[./\-,]\s*(\d{4})\s*", text)
    if not m:
        raise FormError(texts.ERR_DATE)
    day, month, year = map(int, m.groups())
    try:
        return date(year, month, day)
    except ValueError:
        raise FormError(texts.ERR_DATE)


def parse_birth_date(text: str) -> str:
    value = parse_date(text)
    if value > now().date():
        raise FormError(texts.ERR_DATE_FUTURE)
    if value.year < 1920:
        raise FormError(texts.ERR_DATE)
    return value.strftime("%d.%m.%Y")


def normalize_phone(text: str) -> str:
    digits = re.sub(r"\D", "", text)
    if len(digits) == 9:  # 90 123 45 67
        digits = "998" + digits
    if digits.startswith("998") and len(digits) != 12:
        raise FormError(texts.ERR_PHONE)
    if not 10 <= len(digits) <= 15:
        raise FormError(texts.ERR_PHONE)
    return digits


def format_phone(digits: str) -> str:
    if digits.startswith("998") and len(digits) == 12:
        d = digits[3:]
        return f"+998 {d[:2]} {d[2:5]} {d[5:7]} {d[7:]}"
    return "+" + digits


def parse_list(text: str, max_len: int) -> list[str]:
    names = []
    for line in text.splitlines():
        # "1. Ism", "2) Ism", "- Ism" kabi raqamlash va belgilarni olib tashlaymiz
        line = re.sub(r"^\s*(\d+\s*[.)]|[-–—•*])\s*", "", line)
        line = " ".join(line.split())
        if line:
            names.append(line)
    if len(names) < 2:
        raise FormError(texts.ERR_PARTICIPANTS)
    if len(names) > MAX_PARTICIPANTS:
        raise FormError(texts.ERR_PARTICIPANTS_MANY.format(n=MAX_PARTICIPANTS))
    for name in names:
        if len(name) > max_len:
            raise FormError(texts.ERR_LONG.format(n=max_len))
    return names


def parse_video(message: Message) -> dict[str, str]:
    if message.video:
        return {"type": "video", "file_id": message.video.file_id}
    if message.document and (message.document.mime_type or "").startswith("video/"):
        return {"type": "document", "file_id": message.document.file_id}
    text = (message.text or "").strip()
    if re.match(r"https?://\S+$", text):
        return {"type": "link", "url": text[:500]}
    raise FormError(texts.ERR_VIDEO)


def parse_answer(field: Field, message: Message, options: list[str]) -> Any:
    if field.type == "video":
        return parse_video(message)
    if field.type == "phone" and message.contact:
        return normalize_phone(message.contact.phone_number)

    text = (message.text or "").strip()
    if not text:
        raise FormError(texts.ERR_TEXT)

    if field.type == "phone":
        return normalize_phone(text)
    if field.type == "date":
        return parse_birth_date(text)
    if field.type == "list":
        return parse_list(text, field.max_len)
    if field.type == "choice" and options:
        if text not in options:
            raise FormError(texts.ERR_CHOICE)
        return text
    return clean_text(text, field.max_len)


# --- ko'rsatish ---


def display(field: Field, value: Any) -> str:
    """Qiymatni oddiy matn ko'rinishida qaytaradi (HTML ekranlanmagan)."""
    if value in (None, "", []):
        return "—"
    if field.type == "phone":
        return format_phone(value)
    if field.type == "list":
        return "\n".join(f"{i}. {name}" for i, name in enumerate(value, 1))
    if field.type == "video":
        return value["url"] if value["type"] == "link" else "video fayl yuborilgan"
    return str(value)


def summary_html(contest: Contest, kind: str, answers: dict[str, Any]) -> str:
    lines = [
        f"🏆 Tanlov: <b>{escape(contest.title)}</b>",
        f"Turi: <b>{texts.KIND_LABELS[kind]}</b>",
        "",
    ]
    for field in fields_for(kind, contest):
        value = answers.get(field.key)
        if field.type == "list" and value:
            shown = value[:30]
            body = "\n".join(f"   {i}. {escape(name)}" for i, name in enumerate(shown, 1))
            if len(value) > len(shown):
                body += f"\n   … yana {len(value) - len(shown)} nafar"
            lines.append(f"<b>{field.label}</b> ({len(value)} nafar):\n{body}")
        else:
            lines.append(f"<b>{field.label}:</b> {escape(display(field, value))}")
    return "\n".join(lines)
