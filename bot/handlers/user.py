from __future__ import annotations

import re
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message

from .. import keyboards as kb
from .. import texts
from ..config import Config
from ..db import Database
from ..docgen import file_name
from ..services import send_announcement
from .apply import start_application

router = Router(name="user")
router.message.filter(F.chat.type == ChatType.PRIVATE)


@router.message(CommandStart())
async def start(
    message: Message, command: CommandObject, state: FSMContext, db: Database, config: Config
) -> None:
    await state.clear()
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)

    # t.me/<bot>?start=apply_5 — kanal e'lonidagi «Ariza topshirish» tugmasi
    match = re.fullmatch(r"apply_(\d+)", command.args or "")
    if match:
        await start_application(message, state, db, int(match.group(1)))
        return

    await message.answer(
        texts.WELCOME.format(name=escape(user.first_name)),
        reply_markup=kb.main_menu(user.id in config.admin_ids),
    )


@router.message(Command("cancel"))
@router.message(F.text == texts.BTN_CANCEL)
async def cancel(message: Message, state: FSMContext, config: Config) -> None:
    await state.clear()
    await message.answer(
        texts.CANCELLED, reply_markup=kb.main_menu(message.from_user.id in config.admin_ids)
    )


@router.message(StateFilter(None), F.text == texts.BTN_CONTESTS)
async def show_contests(message: Message, db: Database, bot: Bot) -> None:
    contests = await db.accepting_contests()
    if not contests:
        await message.answer(texts.NO_CONTESTS)
        return
    for contest in contests:
        await send_announcement(bot, message.chat.id, contest, kb.apply_button(contest.id))


@router.message(StateFilter(None), F.text == texts.BTN_MY_APPS)
async def my_applications(message: Message, db: Database) -> None:
    apps = await db.user_applications(message.from_user.id)
    if not apps:
        await message.answer(texts.NO_APPS)
        return
    items = [
        f"<b>№{app.id}</b> · {escape(app.contest_title)}\n"
        f"{escape(app.display_name)} — {texts.STATUS[app.status]}"
        for app in apps
    ]
    await message.answer(
        texts.MY_APPS_HEAD + "\n\n".join(items) + "\n" + texts.MY_APPS_HINT,
        reply_markup=kb.my_docs(apps),
    )


@router.callback_query(kb.MyDocCb.filter())
async def send_my_doc(
    callback: CallbackQuery, callback_data: kb.MyDocCb, db: Database, config: Config
) -> None:
    app = await db.get_application(callback_data.app_id)
    path = config.data_dir / app.doc_path if app and app.doc_path else None
    if app is None or app.user_id != callback.from_user.id or path is None or not path.exists():
        await callback.answer(texts.DOC_NOT_FOUND, show_alert=True)
        return
    await callback.answer()
    await callback.message.answer_document(
        FSInputFile(path, filename=file_name(app.id, app.display_name)),
        caption=f"№{app.id} — {texts.STATUS[app.status]}",
    )
