from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery, Message

from .config import Config


class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery, config: Config) -> bool:
        user = event.from_user
        return user is not None and user.id in config.admin_ids
