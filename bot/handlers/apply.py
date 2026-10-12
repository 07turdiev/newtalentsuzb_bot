"""Ariza to'ldirish: tanlov → ishtirok turi → maydonlar ketma-ket → tasdiqlash → yuborish."""

from __future__ import annotations

import asyncio
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message, ReplyKeyboardRemove

from .. import docgen, forms, services
from .. import keyboards as kb
from .. import texts
from ..config import Config, now
from ..db import Contest, Database

log = logging.getLogger(__name__)

router = Router(name="apply")
router.message.filter(F.chat.type == ChatType.PRIVATE)


class ApplyForm(StatesGroup):
    kind = State()
    field = State()
    confirm = State()


async def start_application(message: Message, state: FSMContext, db: Database, contest_id: int) -> None:
    contest = await db.get_contest(contest_id)
    if contest is None or not contest.accepting:
        await message.answer(texts.CONTEST_CLOSED)
        return
    await state.clear()
    await state.set_state(ApplyForm.kind)
    await state.update_data(contest_id=contest.id)
    await message.answer(texts.FORM_STARTED.format(title=escape(contest.title)), reply_markup=kb.cancel_only())
    await message.answer(texts.CHOOSE_KIND, reply_markup=kb.kind_choice())


async def _load(state: FSMContext, db: Database) -> tuple[dict, Contest | None]:
    data = await state.get_data()
    contest = await db.get_contest(data["contest_id"]) if "contest_id" in data else None
    return data, contest


async def _abort(message: Message, state: FSMContext, config: Config) -> None:
    await state.clear()
    await message.answer(
        texts.CONTEST_CLOSED, reply_markup=kb.main_menu(message.chat.id in config.admin_ids)
    )


async def ask_field(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config)
        return
    fields = forms.fields_for(data["kind"], contest)
    step = data["step"]
    if step >= len(fields):
        await show_confirm(message, state, db, config)
        return
    field = fields[step]
    options = forms.options_for(field, contest)
    await message.answer(
        f"<b>{step + 1}/{len(fields)}.</b> {forms.prompt_for(field, options)}",
        reply_markup=kb.field_keyboard(field, options, can_back=step > 0 or data.get("editing", False)),
    )


async def show_confirm(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config)
        return
    await state.set_state(ApplyForm.confirm)
    await message.answer(
        texts.CHECK_DATA + forms.summary_html(contest, data["kind"], data["answers"]),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(texts.CONSENT, reply_markup=kb.confirm())


# --- kirish nuqtalari ---


@router.message(StateFilter(None), F.text == texts.BTN_APPLY)
async def apply_entry(message: Message, state: FSMContext, db: Database) -> None:
    contests = await db.accepting_contests()
    if not contests:
        await message.answer(texts.NO_CONTESTS)
    elif len(contests) == 1:
        await start_application(message, state, db, contests[0].id)
    else:
        await message.answer(texts.CHOOSE_CONTEST, reply_markup=kb.contests_choice(contests))


@router.callback_query(kb.ApplyCb.filter())
async def apply_from_button(
    callback: CallbackQuery, callback_data: kb.ApplyCb, state: FSMContext, db: Database
) -> None:
    await callback.answer()
    await start_application(callback.message, state, db, callback_data.contest_id)


# --- ishtirok turi ---


@router.callback_query(ApplyForm.kind, kb.KindCb.filter())
async def kind_chosen(
    callback: CallbackQuery, callback_data: kb.KindCb, state: FSMContext, db: Database, config: Config
) -> None:
    await callback.answer()
    await callback.message.edit_text(
        f"{texts.CHOOSE_KIND} <b>{texts.KIND_LABELS[callback_data.kind]}</b>"
    )
    await state.update_data(kind=callback_data.kind, step=0, answers={}, editing=False)
    await state.set_state(ApplyForm.field)
    await ask_field(callback.message, state, db, config)


@router.message(ApplyForm.kind)
async def kind_expected(message: Message) -> None:
    await message.answer(texts.USE_BUTTONS)


# --- maydonlar ---


@router.message(ApplyForm.field)
async def field_answer(message: Message, state: FSMContext, db: Database, config: Config) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config)
        return
    fields = forms.fields_for(data["kind"], contest)
    step = min(data["step"], len(fields) - 1)
    field = fields[step]
    editing = data.get("editing", False)

    if message.text == texts.BTN_BACK and (step > 0 or editing):
        if editing:
            await state.update_data(editing=False)
            await show_confirm(message, state, db, config)
        else:
            await state.update_data(step=step - 1)
            await ask_field(message, state, db, config)
        return

    if field.optional and message.text == texts.BTN_SKIP:
        value = None
    else:
        try:
            value = forms.parse_answer(field, message, forms.options_for(field, contest))
        except forms.FormError as error:
            await message.answer(str(error))
            return

    answers = {**data["answers"], field.key: value}
    if editing or step + 1 >= len(fields):
        await state.update_data(answers=answers, editing=False, step=len(fields))
        await show_confirm(message, state, db, config)
    else:
        await state.update_data(answers=answers, step=step + 1)
        await ask_field(message, state, db, config)


# --- tasdiqlash ---


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "edit"))
async def edit_pick(callback: CallbackQuery, state: FSMContext, db: Database) -> None:
    data, contest = await _load(state, db)
    await callback.answer()
    if contest is None:
        return
    await callback.message.edit_text(
        texts.EDIT_WHICH, reply_markup=kb.edit_fields(forms.fields_for(data["kind"], contest))
    )


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "back"))
async def edit_back(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(texts.CONSENT, reply_markup=kb.confirm())


@router.callback_query(ApplyForm.confirm, kb.EditCb.filter())
async def edit_field(
    callback: CallbackQuery, callback_data: kb.EditCb, state: FSMContext, db: Database, config: Config
) -> None:
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(step=callback_data.index, editing=True)
    await state.set_state(ApplyForm.field)
    await ask_field(callback.message, state, db, config)


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "cancel"))
async def confirm_cancel(callback: CallbackQuery, state: FSMContext, config: Config) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
        texts.CANCELLED, reply_markup=kb.main_menu(callback.from_user.id in config.admin_ids)
    )


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "send"))
async def submit(
    callback: CallbackQuery, state: FSMContext, db: Database, config: Config, bot: Bot
) -> None:
    data, contest = await _load(state, db)
    await state.clear()  # ikki marta bosilsa, ikkinchisi e'tiborsiz qoladi
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    menu = kb.main_menu(callback.from_user.id in config.admin_ids)

    if contest is None or not contest.accepting:
        await callback.message.answer(texts.CONTEST_CLOSED, reply_markup=menu)
        return

    answers = {**data["answers"], "consent_at": now().strftime("%d.%m.%Y %H:%M")}
    try:
        app = await db.create_application(contest.id, callback.from_user.id, data["kind"], answers)
    except Exception:
        log.exception("Could not save application")
        await callback.message.answer(texts.SUBMIT_FAILED, reply_markup=menu)
        return

    doc_path = config.data_dir / "applications" / str(contest.id) / docgen.file_name(app.id, app.display_name)
    try:
        await asyncio.to_thread(docgen.render, app.kind, contest.title, app.data, doc_path)
        await db.set_application_doc(app.id, doc_path.relative_to(config.data_dir).as_posix())
    except Exception:
        log.exception("Could not render document for application %s", app.id)
        doc_path = None

    text = texts.SUBMITTED.format(id=app.id)
    if doc_path is not None:
        await callback.message.answer_document(
            FSInputFile(doc_path, filename=doc_path.name), caption=text, reply_markup=menu
        )
    else:
        await callback.message.answer(text, reply_markup=menu)

    await services.notify_new_application(bot, config, app, contest, doc_path)


@router.message(ApplyForm.confirm)
async def confirm_expected(message: Message) -> None:
    await message.answer(texts.USE_BUTTONS)
