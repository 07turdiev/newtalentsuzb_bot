"""Admin panel: tanlov yaratish va e'lon qilish, to'lov rekvizitlari, arizalarni ko'rib chiqish."""

from __future__ import annotations

import asyncio
from datetime import date
from html import escape

from aiogram import Bot, F, Router
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message

from .. import export, forms, services
from .. import keyboards as kb
from .. import texts
from ..config import Config, now
from ..db import Contest, Database
from ..filters import IsAdmin
from ..locales import t

router = Router(name="admin")
router.message.filter(IsAdmin(), F.chat.type == ChatType.PRIVATE)
router.callback_query.filter(IsAdmin())

TELEGRAM_FILE_LIMIT = 49 * 1024 * 1024


class ContestForm(StatesGroup):
    title = State()
    announcement = State()
    deadline = State()
    directions = State()
    ages = State()
    video = State()
    confirm = State()


class EditContest(StatesGroup):
    deadline = State()


class PaymentForm(StatesGroup):
    card = State()
    holder = State()
    amount = State()


# --- panel ---


@router.message(Command("admin"))
@router.message(StateFilter(None), F.text == texts.BTN_ADMIN)
async def admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.ADMIN_PANEL, reply_markup=kb.admin_menu())


@router.callback_query(kb.AdminCb.filter(F.action == "menu"))
async def admin_menu(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.edit_text(texts.ADMIN_PANEL, reply_markup=kb.admin_menu())


@router.callback_query(kb.AdminCb.filter(F.action == "stats"))
async def admin_stats(callback: CallbackQuery, db: Database) -> None:
    users, active = await db.user_counts()
    contests = await db.list_contests(limit=1000)
    await callback.answer()
    await callback.message.edit_text(
        texts.STATS.format(
            users=users, active=active, contests=len(contests), apps=await db.total_applications()
        ),
        reply_markup=kb.back_to_admin(),
    )


@router.callback_query(kb.AdminCb.filter(F.action == "list"))
async def contest_list(callback: CallbackQuery, db: Database) -> None:
    contests = await db.list_contests()
    await callback.answer()
    if not contests:
        await callback.message.edit_text(texts.NO_CONTESTS_ADMIN, reply_markup=kb.back_to_admin())
        return
    await callback.message.edit_text(texts.CONTESTS_HEAD, reply_markup=kb.contests_list(contests))


# --- to'lov ma'lumotlari ---


def _payment_text(payment: dict | None) -> str:
    payment = payment or {}
    return texts.PAYMENT_INFO.format(
        card=f"<code>{escape(payment['card'])}</code>" if payment.get("card") else texts.NOT_SET,
        holder=escape(payment.get("holder") or texts.NOT_SET),
        amount=escape(payment.get("amount") or texts.NOT_SET),
        state=texts.PAYMENT_ON if payment.get("card") else texts.PAYMENT_OFF,
    )


@router.callback_query(kb.AdminCb.filter(F.action == "pay"))
async def payment_info(callback: CallbackQuery, db: Database) -> None:
    payment = await db.get_payment()
    await callback.answer()
    await callback.message.edit_text(_payment_text(payment), reply_markup=kb.payment_settings(payment is not None))


@router.callback_query(kb.AdminCb.filter(F.action == "pay_off"))
async def payment_off(callback: CallbackQuery, db: Database) -> None:
    await db.delete_setting("payment")
    await callback.answer(texts.PAY_DISABLED)
    await callback.message.edit_text(_payment_text(None), reply_markup=kb.payment_settings(False))


@router.callback_query(kb.AdminCb.filter(F.action == "pay_edit"))
async def payment_edit(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(PaymentForm.card)
    await callback.message.answer(texts.PAY_CARD, reply_markup=kb.cancel_only())


@router.message(PaymentForm.card, F.text)
async def payment_card(message: Message, state: FSMContext) -> None:
    try:
        card = forms.parse_card(message.text)
    except forms.FormError as error:
        await message.answer(error.text("uz"))
        return
    await state.update_data(card=card)
    await state.set_state(PaymentForm.holder)
    await message.answer(texts.PAY_HOLDER, reply_markup=kb.skip_cancel())


def _optional_text(text: str) -> str | None:
    if text == texts.BTN_SKIP:
        return None
    text = " ".join(text.split())
    if not 1 <= len(text) <= 200:
        raise forms.FormError("err.long", n=200)
    return text


@router.message(PaymentForm.holder, F.text)
async def payment_holder(message: Message, state: FSMContext) -> None:
    try:
        holder = _optional_text(message.text)
    except forms.FormError:
        await message.answer(texts.PAY_ERR_TEXT)
        return
    await state.update_data(holder=holder)
    await state.set_state(PaymentForm.amount)
    await message.answer(texts.PAY_AMOUNT)


@router.message(PaymentForm.amount, F.text)
async def payment_amount(message: Message, state: FSMContext, db: Database, lang: str) -> None:
    try:
        amount = _optional_text(message.text)
    except forms.FormError:
        await message.answer(texts.PAY_ERR_TEXT)
        return
    data = await state.get_data()
    await state.clear()
    payment = {"card": data["card"], "holder": data.get("holder"), "amount": amount}
    await db.set_setting("payment", payment)
    await message.answer(texts.PAY_SAVED, reply_markup=kb.main_menu(lang, True))
    await message.answer(_payment_text(payment), reply_markup=kb.payment_settings(True))


@router.message(StateFilter(PaymentForm))
async def payment_unexpected(message: Message) -> None:
    await message.answer(texts.NC_UNEXPECTED)


# --- yangi tanlov ---


@router.callback_query(kb.AdminCb.filter(F.action == "new"))
async def new_contest(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await state.set_state(ContestForm.title)
    await callback.message.answer(texts.NC_TITLE, reply_markup=kb.cancel_only())


@router.message(ContestForm.title, F.text)
async def nc_title(message: Message, state: FSMContext) -> None:
    title = " ".join(message.text.split())
    if not 3 <= len(title) <= 150:
        await message.answer(texts.NC_ERR_TITLE)
        return
    await state.update_data(title=title)
    await state.set_state(ContestForm.announcement)
    await message.answer(texts.NC_ANNOUNCEMENT)


@router.message(ContestForm.announcement, F.photo)
async def nc_announcement(message: Message, state: FSMContext) -> None:
    announcement = message.html_text or ""
    if not announcement.strip():
        await message.answer(texts.NC_ERR_CAPTION)
        return
    await state.update_data(announcement=announcement, photo_id=message.photo[-1].file_id)
    await state.set_state(ContestForm.deadline)
    await message.answer(texts.NC_DEADLINE, reply_markup=kb.skip_cancel())


@router.message(ContestForm.announcement)
async def nc_announcement_no_photo(message: Message) -> None:
    await message.answer(texts.NC_ERR_PHOTO)


@router.message(ContestForm.deadline, F.text)
async def nc_deadline(message: Message, state: FSMContext) -> None:
    if message.text == texts.BTN_SKIP:
        deadline = None
    else:
        try:
            deadline = forms.parse_date(message.text)
        except forms.FormError as error:
            await message.answer(error.text("uz"))
            return
        if deadline < now().date():
            await message.answer(texts.NC_ERR_DEADLINE_PAST)
            return
    await state.update_data(deadline=deadline.isoformat() if deadline else None)
    await state.set_state(ContestForm.directions)
    await message.answer(texts.NC_DIRECTIONS)


def _parse_items(text: str) -> list[str]:
    items = [" ".join(line.split()) for line in text.splitlines()]
    items = list(dict.fromkeys(i for i in items if i))  # bo'sh va takrorlarni olib tashlash
    if not items or len(items) > 30 or any(len(i) > 100 for i in items):
        raise ValueError
    return items


@router.message(ContestForm.directions, F.text)
async def nc_directions(message: Message, state: FSMContext) -> None:
    try:
        directions = [] if message.text == texts.BTN_SKIP else _parse_items(message.text)
    except ValueError:
        await message.answer(texts.NC_ERR_LIST_ITEM)
        return
    await state.update_data(directions=directions)
    await state.set_state(ContestForm.ages)
    await message.answer(texts.NC_AGES)


@router.message(ContestForm.ages, F.text)
async def nc_ages(message: Message, state: FSMContext) -> None:
    try:
        ages = [] if message.text == texts.BTN_SKIP else _parse_items(message.text)
    except ValueError:
        await message.answer(texts.NC_ERR_LIST_ITEM)
        return
    await state.update_data(age_categories=ages)
    await state.set_state(ContestForm.video)
    await message.answer(texts.NC_VIDEO, reply_markup=kb.video_choice())


def _draft_contest(data: dict) -> Contest:
    return Contest(
        id=0,
        title=data["title"],
        announcement=data["announcement"],
        photo_id=data["photo_id"],
        deadline=date.fromisoformat(data["deadline"]) if data["deadline"] else None,
        directions=data["directions"],
        age_categories=data["age_categories"],
        require_video=data["require_video"],
        is_open=True,
        created_at="",
    )


def _settings_text(contest: Contest) -> str:
    return (
        f"🏆 <b>{escape(contest.title)}</b>\n"
        f"Muddat: {_deadline_text(contest)}\n"
        f"Yo'nalishlar: {_list_text(contest.directions)}\n"
        f"Yosh toifalari: {_list_text(contest.age_categories)}\n"
        f"Ijro videosi: {texts.VIDEO_REQUIRED if contest.require_video else texts.VIDEO_NOT_REQUIRED}"
    )


@router.callback_query(ContestForm.video, kb.NewContestCb.filter(F.action.in_({"video_yes", "video_no"})))
async def nc_video(
    callback: CallbackQuery, callback_data: kb.NewContestCb, state: FSMContext, bot: Bot
) -> None:
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await state.update_data(
        require_video=callback_data.action == "video_yes", to_channel=False, to_users=False
    )
    await state.set_state(ContestForm.confirm)
    draft = _draft_contest(await state.get_data())

    # Oldindan ko'rish: tanlov hali saqlanmagan, shuning uchun tugmalar botning o'ziga olib boradi
    link = await services.bot_link(bot)
    await services.send_announcement(bot, callback.from_user.id, draft, kb.channel_buttons(link, link))
    await callback.message.answer(
        texts.NC_PREVIEW_HEAD + _settings_text(draft) + texts.NC_PUBLISH_HINT,
        reply_markup=kb.new_contest_publish(False, False),
    )


@router.callback_query(ContestForm.confirm, kb.NewContestCb.filter(F.action.in_({"channel", "broadcast"})))
async def nc_toggle(
    callback: CallbackQuery, callback_data: kb.NewContestCb, state: FSMContext, config: Config
) -> None:
    data = await state.get_data()
    if callback_data.action == "channel":
        if config.channel_id is None:
            await callback.answer(texts.NO_CHANNEL, show_alert=True)
            return
        data["to_channel"] = not data["to_channel"]
    else:
        data["to_users"] = not data["to_users"]
    await state.update_data(to_channel=data["to_channel"], to_users=data["to_users"])
    await callback.answer()
    await callback.message.edit_reply_markup(
        reply_markup=kb.new_contest_publish(data["to_channel"], data["to_users"])
    )


@router.callback_query(ContestForm.confirm, kb.NewContestCb.filter(F.action == "save"))
async def nc_save(
    callback: CallbackQuery, state: FSMContext, db: Database, config: Config, bot: Bot, lang: str
) -> None:
    data = await state.get_data()
    draft = _draft_contest(data)
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    contest_id = await db.create_contest(
        title=draft.title,
        announcement=draft.announcement,
        photo_id=draft.photo_id,
        deadline=draft.deadline,
        directions=draft.directions,
        age_categories=draft.age_categories,
        require_video=draft.require_video,
    )
    contest = await db.get_contest(contest_id)

    report = [texts.NC_SAVED]
    if data.get("to_channel") and config.channel_id is not None:
        try:
            await services.post_to_channel(bot, config, contest)
            report.append(texts.POSTED)
        except TelegramAPIError as error:
            report.append(texts.POST_FAILED.format(error=escape(str(error))))
    if data.get("to_users"):
        services.start_broadcast(bot, db, contest, callback.from_user.id)
        report.append(texts.BROADCAST_STARTED)

    await callback.message.answer("\n".join(report), reply_markup=kb.main_menu(lang, True))
    text, markup = await _card(contest, db, config, bot)
    await callback.message.answer(text, reply_markup=markup)


@router.callback_query(ContestForm.confirm, kb.NewContestCb.filter(F.action == "cancel"))
async def nc_cancel(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(texts.CANCELLED, reply_markup=kb.main_menu(lang, True))


@router.message(StateFilter(ContestForm))
async def nc_unexpected(message: Message) -> None:
    await message.answer(texts.NC_UNEXPECTED)


# --- tanlov kartochkasi ---


def _deadline_text(contest: Contest) -> str:
    return contest.deadline.strftime("%d.%m.%Y") + " gacha" if contest.deadline else texts.DEADLINE_NONE


def _list_text(items: list[str]) -> str:
    return escape(", ".join(items)) if items else texts.LIST_FREE


async def _card(contest: Contest, db: Database, config: Config, bot: Bot):
    stats = await db.contest_stats(contest.id)
    if contest.accepting:
        state = texts.STATE_OPEN
    elif contest.is_open:
        state = texts.STATE_EXPIRED
    else:
        state = texts.STATE_CLOSED
    text = texts.CONTEST_CARD.format(
        title=escape(contest.title),
        state=state,
        deadline=_deadline_text(contest),
        directions=_list_text(contest.directions),
        ages=_list_text(contest.age_categories),
        video=texts.VIDEO_REQUIRED if contest.require_video else texts.VIDEO_NOT_REQUIRED,
        link=await services.deep_link(bot, contest.id),
        **stats,
    )
    return text, kb.contest_card(contest, has_channel=config.channel_id is not None)


async def _get_contest(callback: CallbackQuery, callback_data: kb.ContestCb, db: Database) -> Contest | None:
    contest = await db.get_contest(callback_data.id)
    if contest is None:
        await callback.answer(t("uz", "stale"), show_alert=True)
    return contest


@router.callback_query(kb.ContestCb.filter(F.action == "view"))
async def contest_view(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config, bot: Bot
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await callback.answer()
    text, markup = await _card(contest, db, config, bot)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(kb.ContestCb.filter(F.action == "toggle"))
async def contest_toggle(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config, bot: Bot
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await db.set_contest_open(contest.id, not contest.is_open)
    contest.is_open = not contest.is_open
    await callback.answer(texts.STATE_OPEN if contest.accepting else texts.STATE_CLOSED)
    text, markup = await _card(contest, db, config, bot)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(kb.ContestCb.filter(F.action == "deadline"))
async def contest_deadline_ask(
    callback: CallbackQuery, callback_data: kb.ContestCb, state: FSMContext, db: Database
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await callback.answer()
    await state.set_state(EditContest.deadline)
    await state.update_data(contest_id=contest.id)
    await callback.message.answer(
        texts.EDIT_DEADLINE.format(title=escape(contest.title), current=_deadline_text(contest)),
        reply_markup=kb.skip_cancel(),
    )


@router.message(EditContest.deadline, F.text)
async def contest_deadline_save(
    message: Message, state: FSMContext, db: Database, config: Config, bot: Bot, lang: str
) -> None:
    if message.text == texts.BTN_SKIP:
        deadline = None
    else:
        try:
            deadline = forms.parse_date(message.text)
        except forms.FormError as error:
            await message.answer(error.text("uz"))
            return
        if deadline < now().date():
            await message.answer(texts.NC_ERR_DEADLINE_PAST)
            return
    data = await state.get_data()
    await state.clear()
    await db.set_contest_deadline(data["contest_id"], deadline)
    await message.answer(texts.DEADLINE_SAVED, reply_markup=kb.main_menu(lang, True))
    contest = await db.get_contest(data["contest_id"])
    text, markup = await _card(contest, db, config, bot)
    await message.answer(text, reply_markup=markup)


@router.callback_query(kb.ContestCb.filter(F.action == "preview"))
async def contest_preview(callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, bot: Bot) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await callback.answer()
    markup = kb.channel_buttons(await services.deep_link(bot, contest.id), await services.bot_link(bot))
    await services.send_announcement(bot, callback.from_user.id, contest, markup)


@router.callback_query(kb.ContestCb.filter(F.action == "post"))
async def contest_post(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config, bot: Bot
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    if config.channel_id is None:
        await callback.answer(texts.NO_CHANNEL, show_alert=True)
        return
    try:
        await services.post_to_channel(bot, config, contest)
    except TelegramAPIError as error:
        await callback.answer()
        await callback.message.answer(texts.POST_FAILED.format(error=escape(str(error))))
        return
    await callback.answer(texts.POSTED, show_alert=True)


@router.callback_query(kb.ContestCb.filter(F.action == "bcast"))
async def contest_broadcast_ask(callback: CallbackQuery, callback_data: kb.ContestCb, db: Database) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await callback.answer()
    users = await db.active_users()
    await callback.message.edit_text(
        texts.BROADCAST_CONFIRM.format(n=len(users)), reply_markup=kb.broadcast_confirm(contest.id)
    )


@router.callback_query(kb.ContestCb.filter(F.action == "bcast_ok"))
async def contest_broadcast(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config, bot: Bot
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    services.start_broadcast(bot, db, contest, callback.from_user.id)
    await callback.answer(texts.BROADCAST_STARTED, show_alert=True)
    text, markup = await _card(contest, db, config, bot)
    await callback.message.edit_text(text, reply_markup=markup)


@router.callback_query(kb.ContestCb.filter(F.action == "excel"))
async def contest_excel(callback: CallbackQuery, callback_data: kb.ContestCb, db: Database) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    apps = await db.contest_applications(contest.id)
    if not apps:
        await callback.answer(texts.NO_APPLICATIONS, show_alert=True)
        return
    await callback.answer()
    content = await asyncio.to_thread(export.build_excel, contest, apps)
    name = f"Arizalar_{contest.id}_{now():%Y-%m-%d_%H-%M}.xlsx"
    await callback.message.answer_document(
        BufferedInputFile(content, filename=name), caption=f"📊 {escape(contest.title)} — {len(apps)} ta ariza"
    )


@router.callback_query(kb.ContestCb.filter(F.action == "zip"))
async def contest_zip(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    apps = await db.contest_applications(contest.id)
    if not apps:
        await callback.answer(texts.NO_APPLICATIONS, show_alert=True)
        return
    await callback.answer()
    content = await asyncio.to_thread(export.build_zip, apps, config.data_dir)
    if len(content) > TELEGRAM_FILE_LIMIT:
        await callback.message.answer(texts.ZIP_TOO_BIG.format(id=contest.id))
        return
    name = f"Arizalar_{contest.id}_{now():%Y-%m-%d_%H-%M}.zip"
    await callback.message.answer_document(
        BufferedInputFile(content, filename=name), caption=f"📦 {escape(contest.title)} — {len(apps)} ta ariza"
    )


# --- arizani ko'rib chiqish (admin guruhida yoki shaxsiy chatda) ---


@router.callback_query(kb.ReviewCb.filter())
async def review_application(
    callback: CallbackQuery, callback_data: kb.ReviewCb, db: Database, bot: Bot
) -> None:
    app = await db.get_application(callback_data.app_id)
    if app is None or callback_data.action not in ("accepted", "unpaid", "rejected"):
        await callback.answer(t("uz", "stale"), show_alert=True)
        return
    if app.status == callback_data.action:
        await callback.answer(texts.ALREADY_STATUS)
        return

    await db.set_application_status(app.id, callback_data.action)
    app.status = callback_data.action
    contest = await db.get_contest(app.contest_id)
    await callback.answer(t("uz", f"status.{app.status}"))

    caption = services.admin_caption(app, contest, reviewer=callback.from_user.full_name)
    markup = kb.review(app.id, with_payment=app.receipt is not None)
    message = callback.message
    try:
        if getattr(message, "document", None) or getattr(message, "photo", None):
            await bot.edit_message_caption(
                chat_id=message.chat.id, message_id=message.message_id, caption=caption, reply_markup=markup
            )
        else:
            await bot.edit_message_text(
                caption, chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup
            )
    except TelegramBadRequest:
        pass

    # Ishtirokchiga o'z tilida xabar
    user_lang = await db.get_lang(app.user_id) or "uz"
    title = escape(contest.title)
    if app.status == "unpaid":
        payment = await db.get_payment()
        details = forms.payment_details(payment, user_lang) if payment else ""
        text = t(user_lang, "notify.unpaid", id=app.id, title=title, details=details).strip()
        await services.notify_user(bot, app.user_id, text, kb.receipt_again(app.id, user_lang))
    else:
        text = t(user_lang, f"notify.{app.status}", id=app.id, title=title)
        await services.notify_user(bot, app.user_id, text)
