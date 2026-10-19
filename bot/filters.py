from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from .config import Config
from .db import Database


def is_admin(user_id: int, config: Config, db: Database) -> bool:
    """Asosiy admin (.env dagi ADMIN_IDS) yoki botdan qo'shilgan admin."""
    return user_id in config.admin_ids or user_id in db.admin_ids


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, config: Config, db: Database) -> bool:
        user = event.from_user
        return user is not None and is_admin(user.id, config, db)


class IsOwner(BaseFilter):
    """Faqat asosiy adminlar: adminlar ro'yxatini ular boshqaradi."""

    async def __call__(self, event: Message | CallbackQuery, config: Config) -> bool:
        user = event.from_user
        return user is not None and user.id in config.admin_ids
