"""Ariza to'ldirish: tanlov → ishtirok turi → maydonlar → tasdiqlash → (to'lov cheki) → yuborish."""

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
from ..config import Config, now
from ..db import Contest, Database
from ..locales import t, variants

log = logging.getLogger(__name__)

router = Router(name="apply")
router.message.filter(F.chat.type == ChatType.PRIVATE)

RECEIPT_STATUSES = ("awaiting_payment", "unpaid")


class ApplyForm(StatesGroup):
    kind = State()
    field = State()
    confirm = State()


class ReceiptForm(StatesGroup):
    wait = State()


def _menu(user_id: int, config: Config, lang: str):
    return kb.main_menu(lang, user_id in config.admin_ids)


async def start_application(
    message: Message, state: FSMContext, db: Database, contest_id: int, lang: str
) -> None:
    contest = await db.get_contest(contest_id)
    if contest is None or not contest.accepting:
        await message.answer(t(lang, "contest_closed"))
        return
    await state.clear()
    await state.set_state(ApplyForm.kind)
    await state.update_data(contest_id=contest.id)
    await message.answer(
        t(lang, "form_started", title=escape(contest.title), cancel=t(lang, "btn.cancel")),
        reply_markup=kb.cancel_only(lang),
    )
    await message.answer(t(lang, "choose_kind"), reply_markup=kb.kind_choice(lang))


async def _load(state: FSMContext, db: Database) -> tuple[dict, Contest | None]:
    data = await state.get_data()
    contest = await db.get_contest(data["contest_id"]) if "contest_id" in data else None
    return data, contest


async def _abort(message: Message, state: FSMContext, config: Config, lang: str) -> None:
    await state.clear()
    await message.answer(t(lang, "contest_closed"), reply_markup=_menu(message.chat.id, config, lang))


async def ask_field(message: Message, state: FSMContext, db: Database, config: Config, lang: str) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config, lang)
        return
    fields = forms.fields_for(data["kind"], contest)
    step = data["step"]
    if step >= len(fields):
        await show_confirm(message, state, db, config, lang)
        return
    field = fields[step]
    options = forms.options_for(field, contest)
    await message.answer(
        f"<b>{step + 1}/{len(fields)}.</b> {field.prompt(lang, options)}",
        reply_markup=kb.field_keyboard(field, options, step > 0 or data.get("editing", False), lang),
    )


async def show_confirm(message: Message, state: FSMContext, db: Database, config: Config, lang: str) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config, lang)
        return
    await state.set_state(ApplyForm.confirm)
    await message.answer(
        t(lang, "check_data") + forms.summary_html(contest, data["kind"], data["answers"], lang),
        reply_markup=ReplyKeyboardRemove(),
    )
    payment = await db.get_payment()
    await message.answer(t(lang, "consent"), reply_markup=kb.confirm(lang, with_payment=payment is not None))


# --- kirish nuqtalari ---


@router.message(StateFilter(None), F.text.in_(variants("btn.apply")))
async def apply_entry(message: Message, state: FSMContext, db: Database, lang: str) -> None:
    contests = await db.accepting_contests()
    if not contests:
        await message.answer(t(lang, "no_contests"))
    elif len(contests) == 1:
        # Bitta tanlov bo'lsa — tanlatmasdan o'shanga o'tamiz
        await start_application(message, state, db, contests[0].id, lang)
    else:
        await message.answer(t(lang, "choose_contest"), reply_markup=kb.contests_choice(contests))


@router.callback_query(kb.ApplyCb.filter())
async def apply_from_button(
    callback: CallbackQuery, callback_data: kb.ApplyCb, state: FSMContext, db: Database, lang: str
) -> None:
    await callback.answer()
    await start_application(callback.message, state, db, callback_data.contest_id, lang)


# --- ishtirok turi ---


@router.callback_query(ApplyForm.kind, kb.KindCb.filter())
async def kind_chosen(
    callback: CallbackQuery, callback_data: kb.KindCb, state: FSMContext, db: Database, config: Config, lang: str
) -> None:
    await callback.answer()
    await callback.message.edit_text(
        f"{t(lang, 'choose_kind')} <b>{t(lang, f'kind.{callback_data.kind}')}</b>"
    )
    await state.update_data(kind=callback_data.kind, step=0, answers={}, editing=False)
    await state.set_state(ApplyForm.field)
    await ask_field(callback.message, state, db, config, lang)


@router.message(ApplyForm.kind)
async def kind_expected(message: Message, lang: str) -> None:
    await message.answer(t(lang, "use_buttons"))


# --- maydonlar ---


@router.message(ApplyForm.field)
async def field_answer(message: Message, state: FSMContext, db: Database, config: Config, lang: str) -> None:
    data, contest = await _load(state, db)
    if contest is None:
        await _abort(message, state, config, lang)
        return
    fields = forms.fields_for(data["kind"], contest)
    step = min(data["step"], len(fields) - 1)
    field = fields[step]
    editing = data.get("editing", False)

    if message.text in variants("btn.back") and (step > 0 or editing):
        if editing:
            await state.update_data(editing=False)
            await show_confirm(message, state, db, config, lang)
        else:
            await state.update_data(step=step - 1)
            await ask_field(message, state, db, config, lang)
        return

    if field.optional and message.text in variants("btn.skip"):
        value = None
    else:
        try:
            value = forms.parse_answer(field, message, forms.options_for(field, contest))
        except forms.FormError as error:
            await message.answer(error.text(lang))
            return

    answers = {**data["answers"], field.key: value}
    if editing or step + 1 >= len(fields):
        await state.update_data(answers=answers, editing=False, step=len(fields))
        await show_confirm(message, state, db, config, lang)
    else:
        await state.update_data(answers=answers, step=step + 1)
        await ask_field(message, state, db, config, lang)


# --- tasdiqlash ---


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "edit"))
async def edit_pick(callback: CallbackQuery, state: FSMContext, db: Database, lang: str) -> None:
    data, contest = await _load(state, db)
    await callback.answer()
    if contest is None:
        return
    await callback.message.edit_text(
        t(lang, "edit_which"), reply_markup=kb.edit_fields(forms.fields_for(data["kind"], contest), lang)
    )


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "back"))
async def edit_back(callback: CallbackQuery, db: Database, lang: str) -> None:
    await callback.answer()
    payment = await db.get_payment()
    await callback.message.edit_text(t(lang, "consent"), reply_markup=kb.confirm(lang, payment is not None))


@router.callback_query(ApplyForm.confirm, kb.EditCb.filter())
async def edit_field(
    callback: CallbackQuery, callback_data: kb.EditCb, state: FSMContext, db: Database, config: Config, lang: str
) -> None:
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(step=callback_data.index, editing=True)
    await state.set_state(ApplyForm.field)
    await ask_field(callback.message, state, db, config, lang)


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "cancel"))
async def confirm_cancel(callback: CallbackQuery, state: FSMContext, config: Config, lang: str) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(t(lang, "cancelled"), reply_markup=_menu(callback.from_user.id, config, lang))


@router.callback_query(ApplyForm.confirm, kb.ConfirmCb.filter(F.action == "send"))
async def submit(
    callback: CallbackQuery, state: FSMContext, db: Database, config: Config, bot: Bot, lang: str
) -> None:
    data, contest = await _load(state, db)
    await state.clear()  # ikki marta bosilsa, ikkinchisi e'tiborsiz qoladi
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    menu = _menu(callback.from_user.id, config, lang)

    if contest is None or not contest.accepting:
        await callback.message.answer(t(lang, "contest_closed"), reply_markup=menu)
        return

    payment = await db.get_payment()
    answers = {**data["answers"], "consent_at": now().strftime("%d.%m.%Y %H:%M")}
    try:
        app = await db.create_application(
            contest.id, callback.from_user.id, data["kind"], answers,
            status="awaiting_payment" if payment else "new",
        )
    except Exception:
        log.exception("Could not save application")
        await callback.message.answer(t(lang, "submit_failed"), reply_markup=menu)
        return

    doc_path = config.data_dir / "applications" / str(contest.id) / docgen.file_name(app.id, app.display_name)
    try:
        await asyncio.to_thread(docgen.render, app.kind, contest.title, app.data, doc_path)
        await db.set_application_doc(app.id, doc_path.relative_to(config.data_dir).as_posix())
    except Exception:
        log.exception("Could not render document for application %s", app.id)
        doc_path = None

    if payment:
        # Ariza saqlandi, endi to'lov cheki kutiladi; adminga chek kelgach yuboriladi
        await state.set_state(ReceiptForm.wait)
        await state.update_data(app_id=app.id)
        await callback.message.answer(
            t(lang, "payment", id=app.id, details=forms.payment_details(payment, lang)),
            reply_markup=kb.cancel_only(lang),
        )
        return

    text = t(lang, "submitted", id=app.id)
    if doc_path is not None:
        await callback.message.answer_document(
            FSInputFile(doc_path, filename=doc_path.name), caption=text, reply_markup=menu
        )
    else:
        await callback.message.answer(text, reply_markup=menu)
    await services.notify_new_application(bot, config, app, contest, doc_path)


@router.message(ApplyForm.confirm)
async def confirm_expected(message: Message, lang: str) -> None:
    await message.answer(t(lang, "use_buttons"))


# --- to'lov cheki ---


@router.callback_query(kb.ReceiptCb.filter())
async def receipt_start(
    callback: CallbackQuery, callback_data: kb.ReceiptCb, state: FSMContext, db: Database, lang: str
) -> None:
    app = await db.get_application(callback_data.app_id)
    if app is None or app.user_id != callback.from_user.id:
        await callback.answer(t(lang, "stale"), show_alert=True)
        return
    if app.status not in RECEIPT_STATUSES:
        await callback.answer(t(lang, "receipt.not_needed"), show_alert=True)
        return
    await callback.answer()
    await state.clear()
    await state.set_state(ReceiptForm.wait)
    await state.update_data(app_id=app.id)
    payment = await db.get_payment()
    details = forms.payment_details(payment, lang) if payment else ""
    await callback.message.answer(
        t(lang, "receipt.prompt", id=app.id, details=details).strip(),
        reply_markup=kb.cancel_only(lang),
    )


@router.message(ReceiptForm.wait, F.photo | F.document)
async def receipt_received(
    message: Message, state: FSMContext, db: Database, config: Config, bot: Bot, lang: str
) -> None:
    app_id = (await state.get_data()).get("app_id")
    await state.clear()
    menu = _menu(message.from_user.id, config, lang)
    app = await db.get_application(app_id) if app_id else None
    if app is None or app.user_id != message.from_user.id or app.status not in RECEIPT_STATUSES:
        await message.answer(t(lang, "receipt.not_needed"), reply_markup=menu)
        return

    if message.photo:
        receipt = {"type": "photo", "file_id": message.photo[-1].file_id}
    else:
        receipt = {"type": "document", "file_id": message.document.file_id}
    resubmitted = app.status == "unpaid"
    await db.set_receipt(app.id, receipt)
    app = await db.get_application(app.id)
    contest = await db.get_contest(app.contest_id)

    doc_path = config.data_dir / app.doc_path if app.doc_path else None
    if doc_path is not None and not doc_path.exists():
        doc_path = None
    text = t(lang, "receipt.ok", id=app.id)
    if doc_path is not None and not resubmitted:
        await message.answer_document(FSInputFile(doc_path, filename=doc_path.name), caption=text, reply_markup=menu)
    else:
        await message.answer(text, reply_markup=menu)
    await services.notify_new_application(bot, config, app, contest, doc_path, resubmitted=resubmitted)


@router.message(ReceiptForm.wait)
async def receipt_expected(message: Message, lang: str) -> None:
    await message.answer(t(lang, "receipt.expected"))
