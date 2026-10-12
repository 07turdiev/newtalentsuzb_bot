from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from .. import texts

router = Router(name="common")
# Boshqa routerlar ishlatmagan eski tugmalar uchun — eng oxirida ulanadi
fallback_router = Router(name="fallback")


@router.message(Command("id"))
async def show_id(message: Message) -> None:
    """Sozlash uchun: foydalanuvchi va chat ID sini ko'rsatadi (guruhda ham ishlaydi)."""
    await message.answer(
        f"Sizning ID: <code>{message.from_user.id}</code>\n"
        f"Shu chat ID: <code>{message.chat.id}</code>"
    )


@fallback_router.callback_query()
async def stale_button(callback: CallbackQuery) -> None:
    await callback.answer(texts.STALE_BUTTON)
