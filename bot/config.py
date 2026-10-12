from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"

# Toshkent vaqti (UTC+5, yozgi vaqtga o'tilmaydi)
TZ = timezone(timedelta(hours=5))


def now() -> datetime:
    return datetime.now(TZ)


@dataclass(frozen=True)
class Config:
    bot_token: str
    admin_ids: frozenset[int]
    admin_chat_id: int | None
    channel_id: int | str | None
    data_dir: Path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "bot.db"

    @property
    def review_chats(self) -> list[int]:
        """Yangi arizalar yuboriladigan chatlar: admin guruhi yoki har bir admin."""
        if self.admin_chat_id:
            return [self.admin_chat_id]
        return sorted(self.admin_ids)


def _int_or_none(value: str, name: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        raise SystemExit(f"{name} raqam bo'lishi kerak, hozir: {value!r}")


def load_config() -> Config:
    load_dotenv(BASE_DIR / ".env")

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise SystemExit("BOT_TOKEN topilmadi: .env faylini to'ldiring (namuna: .env.example)")

    admin_ids = frozenset(
        int(x) for x in re.split(r"[,\s]+", os.getenv("ADMIN_IDS", "")) if x
    )
    if not admin_ids:
        raise SystemExit("ADMIN_IDS bo'sh: kamida bitta admin Telegram ID sini kiriting")

    channel = os.getenv("CHANNEL_ID", "").strip()
    channel_id: int | str | None
    if not channel:
        channel_id = None
    elif channel.lstrip("-").isdigit():
        channel_id = int(channel)
    else:
        channel_id = channel if channel.startswith("@") else "@" + channel

    data_dir = Path(os.getenv("DATA_DIR") or BASE_DIR / "data")
    data_dir.mkdir(parents=True, exist_ok=True)

    return Config(
        bot_token=token,
        admin_ids=admin_ids,
        admin_chat_id=_int_or_none(os.getenv("ADMIN_CHAT_ID", ""), "ADMIN_CHAT_ID"),
        channel_id=channel_id,
        data_dir=data_dir,
    )
