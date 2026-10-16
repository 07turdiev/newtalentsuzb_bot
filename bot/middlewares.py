from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from .locales import DEFAULT_LANG


class LangMiddleware(BaseMiddleware):
    """Handlerlarga foydalanuvchi tilini `lang` argumenti sifatida beradi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user: User | None = data.get("event_from_user")
        lang = await data["db"].get_lang(user.id) if user else None
        data["lang"] = lang or DEFAULT_LANG
        return await handler(event, data)
