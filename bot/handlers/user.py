from __future__ import annotations

import re
from html import escape

from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, Message, User

from .. import keyboards as kb
from ..config import Config
from ..db import Database
from ..docgen import file_name
from ..locales import CHOOSE_LANG, LANGS, t, variants
from .apply import ReceiptForm, start_application

router = Router(name="user")
router.message.filter(F.chat.type == ChatType.PRIVATE)


async def send_welcome(message: Message, user: User, db: Database, config: Config, lang: str) -> None:
    contests = await db.accepting_contests()
    if not contests:
        key = "welcome.none"
    elif len(contests) == 1:
        key = "welcome.one"
    else:
        key = "welcome.many"
    titles = ", ".join(f"<b>«{escape(c.title)}»</b>" for c in contests)
    await message.answer(
        t(lang, key, name=escape(user.first_name), contests=titles, btn=t(lang, "btn.apply")),
        reply_markup=kb.main_menu(lang, user.id in config.admin_ids),
    )


@router.message(CommandStart())
async def start(
    message: Message, command: CommandObject, state: FSMContext, db: Database, config: Config
) -> None:
    await state.clear()
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)

    # t.me/<bot>?start=apply_5 — kanal e'lonidagi «Ariza yuborish» tugmasi
    match = re.fullmatch(r"apply_(\d+)", command.args or "")
    contest_id = int(match.group(1)) if match else None

    lang = await db.get_lang(user.id)
    if lang is None:
        # Birinchi kirish: avval til tanlanadi, keyin ariza (agar havola orqali kelgan bo'lsa)
        await state.update_data(pending_contest=contest_id)
        await message.answer(CHOOSE_LANG, reply_markup=kb.languages())
        return

    if contest_id is not None:
        await start_application(message, state, db, contest_id, lang)
        return
    await send_welcome(message, user, db, config, lang)


@router.message(StateFilter(None), F.text.in_(variants("btn.lang")))
async def change_language(message: Message) -> None:
    await message.answer(CHOOSE_LANG, reply_markup=kb.languages())


@router.callback_query(kb.LangCb.filter())
async def language_chosen(
    callback: CallbackQuery, callback_data: kb.LangCb, state: FSMContext, db: Database, config: Config
) -> None:
    lang = callback_data.code if callback_data.code in LANGS else "uz"
    await db.set_lang(callback.from_user.id, lang)
    await callback.answer()
    await callback.message.edit_text(f"{LANGS[lang]}\n{t(lang, 'lang_set')}")

    pending = (await state.get_data()).get("pending_contest")
    if pending is not None:
        await start_application(callback.message, state, db, pending, lang)
    elif await state.get_state() is None:
        await send_welcome(callback.message, callback.from_user, db, config, lang)


@router.message(Command("cancel"))
@router.message(F.text.in_(variants("btn.cancel")))
async def cancel(message: Message, state: FSMContext, config: Config, lang: str) -> None:
    waiting_receipt = await state.get_state() == ReceiptForm.wait.state
    await state.clear()
    if waiting_receipt:
        text = t(lang, "receipt.later", my_apps=t(lang, "btn.my_apps"))
    else:
        text = t(lang, "cancelled")
    await message.answer(text, reply_markup=kb.main_menu(lang, message.from_user.id in config.admin_ids))


@router.message(StateFilter(None), F.text.in_(variants("btn.my_apps")))
async def my_applications(message: Message, db: Database, lang: str) -> None:
    apps = await db.user_applications(message.from_user.id)
    if not apps:
        await message.answer(t(lang, "no_apps"))
        return
    items = [
        f"<b>№{app.id}</b> · {escape(app.contest_title)}\n"
        f"{escape(app.display_name)} — {t(lang, f'status.{app.status}')}"
        for app in apps
    ]
    await message.answer(
        t(lang, "my_apps.head") + "\n\n".join(items) + "\n\n" + t(lang, "my_apps.hint"),
        reply_markup=kb.my_apps(apps, lang),
    )


@router.callback_query(kb.MyDocCb.filter())
async def send_my_doc(
    callback: CallbackQuery, callback_data: kb.MyDocCb, db: Database, config: Config, lang: str
) -> None:
    app = await db.get_application(callback_data.app_id)
    path = config.data_dir / app.doc_path if app and app.doc_path else None
    if app is None or app.user_id != callback.from_user.id or path is None or not path.exists():
        await callback.answer(t(lang, "doc_not_found"), show_alert=True)
        return
    await callback.answer()
    await callback.message.answer_document(
        FSInputFile(path, filename=file_name(app.id, app.display_name)),
        caption=f"№{app.id} — {t(lang, f'status.{app.status}')}",
    )
