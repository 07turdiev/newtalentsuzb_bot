"""Admin panel: tanlov yaratish va e'lon qilish, arizalarni ko'rish, qabul qilish/rad etish."""

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


@router.message(ContestForm.announcement, F.text | F.photo)
async def nc_announcement(message: Message, state: FSMContext) -> None:
    announcement = message.html_text or ""
    photo_id = message.photo[-1].file_id if message.photo else None
    if not announcement.strip() and photo_id is None:
        await message.answer(texts.NC_ERR_ANNOUNCEMENT)
        return
    await state.update_data(announcement=announcement, photo_id=photo_id)
    await state.set_state(ContestForm.deadline)
    await message.answer(texts.NC_DEADLINE, reply_markup=kb.skip_cancel())


@router.message(ContestForm.deadline, F.text)
async def nc_deadline(message: Message, state: FSMContext) -> None:
    if message.text == texts.BTN_SKIP:
        deadline = None
    else:
        try:
            deadline = forms.parse_date(message.text)
        except forms.FormError as error:
            await message.answer(str(error))
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
        raise forms.FormError(texts.NC_ERR_LIST_ITEM)
    return items


@router.message(ContestForm.directions, F.text)
async def nc_directions(message: Message, state: FSMContext) -> None:
    try:
        directions = [] if message.text == texts.BTN_SKIP else _parse_items(message.text)
    except forms.FormError as error:
        await message.answer(str(error))
        return
    await state.update_data(directions=directions)
    await state.set_state(ContestForm.ages)
    await message.answer(texts.NC_AGES)


@router.message(ContestForm.ages, F.text)
async def nc_ages(message: Message, state: FSMContext) -> None:
    try:
        ages = [] if message.text == texts.BTN_SKIP else _parse_items(message.text)
    except forms.FormError as error:
        await message.answer(str(error))
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
    await state.update_data(require_video=callback_data.action == "video_yes")
    await state.set_state(ContestForm.confirm)
    draft = _draft_contest(await state.get_data())

    # Oldindan ko'rish: tanlov hali saqlanmagan, shuning uchun tugma botning o'ziga olib boradi
    me = await bot.me()
    await services.send_announcement(bot, callback.from_user.id, draft, kb.apply_link(f"https://t.me/{me.username}"))
    await callback.message.answer(
        texts.NC_PREVIEW_HEAD + _settings_text(draft), reply_markup=kb.new_contest_confirm()
    )


@router.callback_query(ContestForm.confirm, kb.NewContestCb.filter(F.action == "save"))
async def nc_save(
    callback: CallbackQuery, state: FSMContext, db: Database, config: Config, bot: Bot
) -> None:
    draft = _draft_contest(await state.get_data())
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
    await callback.message.answer(texts.NC_SAVED, reply_markup=kb.main_menu(True))
    contest = await db.get_contest(contest_id)
    text, markup = await _card(contest, db, config, bot)
    await callback.message.answer(text, reply_markup=markup)


@router.callback_query(ContestForm.confirm, kb.NewContestCb.filter(F.action == "cancel"))
async def nc_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(texts.CANCELLED, reply_markup=kb.main_menu(True))


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
        await callback.answer(texts.STALE_BUTTON, show_alert=True)
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
    message: Message, state: FSMContext, db: Database, config: Config, bot: Bot
) -> None:
    if message.text == texts.BTN_SKIP:
        deadline = None
    else:
        try:
            deadline = forms.parse_date(message.text)
        except forms.FormError as error:
            await message.answer(str(error))
            return
        if deadline < now().date():
            await message.answer(texts.NC_ERR_DEADLINE_PAST)
            return
    data = await state.get_data()
    await state.clear()
    await db.set_contest_deadline(data["contest_id"], deadline)
    await message.answer(texts.DEADLINE_SAVED, reply_markup=kb.main_menu(True))
    contest = await db.get_contest(data["contest_id"])
    text, markup = await _card(contest, db, config, bot)
    await message.answer(text, reply_markup=markup)


@router.callback_query(kb.ContestCb.filter(F.action == "preview"))
async def contest_preview(callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, bot: Bot) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    await callback.answer()
    link = await services.deep_link(bot, contest.id)
    await services.send_announcement(bot, callback.from_user.id, contest, kb.apply_link(link))


@router.callback_query(kb.ContestCb.filter(F.action == "post"))
async def contest_post(
    callback: CallbackQuery, callback_data: kb.ContestCb, db: Database, config: Config, bot: Bot
) -> None:
    if not (contest := await _get_contest(callback, callback_data, db)):
        return
    if config.channel_id is None:
        await callback.answer(texts.NO_CHANNEL, show_alert=True)
        return
    link = await services.deep_link(bot, contest.id)
    try:
        await services.send_announcement(bot, config.channel_id, contest, kb.apply_link(link))
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
    users = await db.active_user_ids()
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
    if app is None:
        await callback.answer(texts.STALE_BUTTON, show_alert=True)
        return
    if app.status == callback_data.action:
        await callback.answer(texts.ALREADY_STATUS)
        return

    await db.set_application_status(app.id, callback_data.action)
    app.status = callback_data.action
    contest = await db.get_contest(app.contest_id)
    await callback.answer(texts.STATUS[app.status])

    caption = services.admin_caption(app, contest, reviewer=callback.from_user.full_name)
    try:
        if getattr(callback.message, "document", None) or getattr(callback.message, "photo", None):
            await bot.edit_message_caption(
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                caption=caption,
                reply_markup=kb.review(app.id),
            )
        else:
            await bot.edit_message_text(
                caption,
                chat_id=callback.message.chat.id,
                message_id=callback.message.message_id,
                reply_markup=kb.review(app.id),
            )
    except TelegramBadRequest:
        pass

    await services.notify_user(
        bot, app.user_id, texts.USER_STATUS[app.status].format(id=app.id, title=escape(contest.title))
    )
