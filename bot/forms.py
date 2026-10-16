"""Ariza shakli maydonlari, ularni tekshirish va ko'rsatish.

Maydon nomlari va savollar matni locales.py da (f.<kalit>, f.<kalit>.prompt).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from html import escape
from typing import Any

from aiogram.types import Message

from .config import now
from .db import Contest
from .locales import t

MAX_PARTICIPANTS = 100


@dataclass(frozen=True)
class Field:
    key: str
    type: str = "text"  # text | date | choice | phone | list | video
    optional: bool = False
    max_len: int = 200

    def label(self, lang: str) -> str:
        return t(lang, f"f.{self.key}")

    def prompt(self, lang: str, options: list[str]) -> str:
        if self.type == "choice" and not options:
            return t(lang, f"f.{self.key}.free")
        if self.type == "phone":
            text = t(lang, "f.phone.prompt", btn=t(lang, "btn.phone"))
        else:
            text = t(lang, f"f.{self.key}.prompt")
        if self.optional:
            text += t(lang, "optional_hint", skip=t(lang, "btn.skip"))
        return text


FULL_NAME = Field("full_name")
BIRTH_DATE = Field("birth_date", type="date")
TEAM_NAME = Field("team_name")
PARTICIPANTS = Field("participants", type="list", max_len=150)
INSTITUTION = Field("institution", optional=True, max_len=300)
DIRECTION = Field("direction", type="choice")
AGE_CATEGORY = Field("age_category", type="choice")
PIECE = Field("piece", max_len=500)
TEACHER = Field("teacher", optional=True)
ACCOMPANIST = Field("accompanist", optional=True)
PARENTS = Field("parents", optional=True, max_len=300)
HEAD = Field("head", optional=True)
PHONE = Field("phone", type="phone")
VIDEO = Field("video", type="video")

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


# --- tekshirish ---


class FormError(Exception):
    """Tekshiruv xatosi: key — locales.py dagi xabar kaliti."""

    def __init__(self, key: str, **params: Any) -> None:
        super().__init__(key)
        self.key = key
        self.params = params

    def text(self, lang: str) -> str:
        return t(lang, self.key, **self.params)


def clean_text(text: str, max_len: int, min_len: int = 2) -> str:
    text = " ".join(text.split())
    if len(text) < min_len:
        raise FormError("err.short")
    if len(text) > max_len:
        raise FormError("err.long", n=max_len)
    return text


def parse_date(text: str) -> date:
    m = re.fullmatch(r"\s*(\d{1,2})\s*[./\-,]\s*(\d{1,2})\s*[./\-,]\s*(\d{4})\s*", text)
    if not m:
        raise FormError("err.date")
    day, month, year = map(int, m.groups())
    try:
        return date(year, month, day)
    except ValueError:
        raise FormError("err.date")


def parse_birth_date(text: str) -> str:
    value = parse_date(text)
    if value > now().date():
        raise FormError("err.date_future")
    if value.year < 1920:
        raise FormError("err.date")
    return value.strftime("%d.%m.%Y")


def normalize_phone(text: str) -> str:
    digits = re.sub(r"\D", "", text)
    if len(digits) == 9:  # 90 123 45 67
        digits = "998" + digits
    if digits.startswith("998") and len(digits) != 12:
        raise FormError("err.phone")
    if not 10 <= len(digits) <= 15:
        raise FormError("err.phone")
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
        raise FormError("err.participants")
    if len(names) > MAX_PARTICIPANTS:
        raise FormError("err.participants_many", n=MAX_PARTICIPANTS)
    for name in names:
        if len(name) > max_len:
            raise FormError("err.long", n=max_len)
    return names


def parse_video(message: Message) -> dict[str, str]:
    if message.video:
        return {"type": "video", "file_id": message.video.file_id}
    if message.document and (message.document.mime_type or "").startswith("video/"):
        return {"type": "document", "file_id": message.document.file_id}
    text = (message.text or "").strip()
    if re.match(r"https?://\S+$", text):
        return {"type": "link", "url": text[:500]}
    raise FormError("err.video")


def parse_answer(field: Field, message: Message, options: list[str]) -> Any:
    if field.type == "video":
        return parse_video(message)
    if field.type == "phone" and message.contact:
        return normalize_phone(message.contact.phone_number)

    text = (message.text or "").strip()
    if not text:
        raise FormError("err.text")

    if field.type == "phone":
        return normalize_phone(text)
    if field.type == "date":
        return parse_birth_date(text)
    if field.type == "list":
        return parse_list(text, field.max_len)
    if field.type == "choice" and options:
        if text not in options:
            raise FormError("err.choice")
        return text
    return clean_text(text, field.max_len)


# --- ko'rsatish ---


def display(field: Field, value: Any, lang: str = "uz") -> str:
    """Qiymatni oddiy matn ko'rinishida qaytaradi (HTML ekranlanmagan)."""
    if value in (None, "", []):
        return "—"
    if field.type == "phone":
        return format_phone(value)
    if field.type == "list":
        return "\n".join(f"{i}. {name}" for i, name in enumerate(value, 1))
    if field.type == "video":
        return value["url"] if value["type"] == "link" else t(lang, "video_sent")
    return str(value)


def summary_html(contest: Contest, kind: str, answers: dict[str, Any], lang: str) -> str:
    lines = [
        f"🏆 {t(lang, 'summary.contest')}: <b>{escape(contest.title)}</b>",
        f"{t(lang, 'summary.kind')}: <b>{t(lang, f'kind.{kind}')}</b>",
        "",
    ]
    for field in fields_for(kind, contest):
        value = answers.get(field.key)
        label = field.label(lang)
        if field.type == "list" and value:
            shown = value[:30]
            body = "\n".join(f"   {i}. {escape(name)}" for i, name in enumerate(shown, 1))
            if len(value) > len(shown):
                body += "\n   " + t(lang, "summary.more", n=len(value) - len(shown))
            lines.append(f"<b>{label}</b> ({len(value)} {t(lang, 'summary.persons')}):\n{body}")
        else:
            lines.append(f"<b>{label}:</b> {escape(display(field, value, lang))}")
    return "\n".join(lines)


def payment_details(payment: dict[str, str], lang: str) -> str:
    """To'lov rekvizitlari (HTML): summa, karta raqami, karta egasi."""
    lines = []
    if payment.get("amount"):
        lines.append(f"{t(lang, 'pay.amount')}: <b>{escape(payment['amount'])}</b>")
    lines.append(f"{t(lang, 'pay.card')}: <code>{escape(payment['card'])}</code>")
    if payment.get("holder"):
        lines.append(f"{t(lang, 'pay.holder')}: {escape(payment['holder'])}")
    return "\n".join(lines)


def parse_card(text: str) -> str:
    """Karta raqamini tekshiradi va 4 tadan guruhlab qaytaradi: 8600 1234 5678 9012."""
    digits = re.sub(r"\D", "", text)
    if not 16 <= len(digits) <= 19:
        raise FormError("err.card")
    return " ".join(digits[i : i + 4] for i in range(0, len(digits), 4))
