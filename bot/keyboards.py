from __future__ import annotations

from collections.abc import Sequence

from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import texts
from .db import Application, Contest
from .forms import Field


class ApplyCb(CallbackData, prefix="ap"):
    contest_id: int


class KindCb(CallbackData, prefix="kd"):
    kind: str


class ConfirmCb(CallbackData, prefix="cf"):
    action: str  # send | edit | back | cancel


class EditCb(CallbackData, prefix="ed"):
    index: int


class MyDocCb(CallbackData, prefix="md"):
    app_id: int


class AdminCb(CallbackData, prefix="ad"):
    action: str  # menu | new | list | stats


class NewContestCb(CallbackData, prefix="nc"):
    action: str  # video_yes | video_no | save | cancel


class ContestCb(CallbackData, prefix="ct"):
    action: str
    id: int


class ReviewCb(CallbackData, prefix="rv"):
    action: str  # accepted | rejected
    app_id: int


def _reply(rows: list[list[KeyboardButton]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _btn(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


# --- foydalanuvchi ---


def main_menu(is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [[_btn(texts.BTN_APPLY)], [_btn(texts.BTN_CONTESTS), _btn(texts.BTN_MY_APPS)]]
    if is_admin:
        rows.append([_btn(texts.BTN_ADMIN)])
    return _reply(rows)


def cancel_only() -> ReplyKeyboardMarkup:
    return _reply([[_btn(texts.BTN_CANCEL)]])


def skip_cancel() -> ReplyKeyboardMarkup:
    return _reply([[_btn(texts.BTN_SKIP)], [_btn(texts.BTN_CANCEL)]])


def field_keyboard(field: Field, options: Sequence[str], can_back: bool) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = []
    if field.type == "choice" and options:
        per_row = 2 if all(len(o) <= 18 for o in options) else 1
        for i in range(0, len(options), per_row):
            rows.append([_btn(o) for o in options[i : i + per_row]])
    if field.type == "phone":
        rows.append([KeyboardButton(text=texts.BTN_PHONE, request_contact=True)])
    if field.optional:
        rows.append([_btn(texts.BTN_SKIP)])
    rows.append([_btn(texts.BTN_BACK), _btn(texts.BTN_CANCEL)] if can_back else [_btn(texts.BTN_CANCEL)])
    return _reply(rows)


def apply_button(contest_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=texts.BTN_APPLY, callback_data=ApplyCb(contest_id=contest_id).pack()
        )]]
    )


def apply_link(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=texts.BTN_APPLY, url=url)]])


def contests_choice(contests: Sequence[Contest]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for contest in contests:
        builder.button(text=contest.title, callback_data=ApplyCb(contest_id=contest.id))
    builder.adjust(1)
    return builder.as_markup()


def kind_choice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for kind, label in texts.KIND_LABELS.items():
        builder.button(text=label, callback_data=KindCb(kind=kind))
    builder.adjust(1)
    return builder.as_markup()


def confirm() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_CONFIRM, callback_data=ConfirmCb(action="send"))
    builder.button(text=texts.BTN_EDIT, callback_data=ConfirmCb(action="edit"))
    builder.button(text=texts.BTN_CANCEL, callback_data=ConfirmCb(action="cancel"))
    builder.adjust(1, 2)
    return builder.as_markup()


def edit_fields(fields: Sequence[Field]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, field in enumerate(fields):
        builder.button(text=field.label, callback_data=EditCb(index=index))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=texts.BTN_BACK, callback_data=ConfirmCb(action="back").pack()))
    return builder.as_markup()


def my_docs(apps: Sequence[Application]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for app in apps:
        if app.doc_path:
            builder.button(text=f"📄 №{app.id}", callback_data=MyDocCb(app_id=app.id))
    builder.adjust(4)
    return builder.as_markup()


# --- admin ---


def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_NEW_CONTEST, callback_data=AdminCb(action="new"))
    builder.button(text=texts.BTN_CONTEST_LIST, callback_data=AdminCb(action="list"))
    builder.button(text=texts.BTN_STATS, callback_data=AdminCb(action="stats"))
    builder.adjust(1)
    return builder.as_markup()


def back_to_admin() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_TO_MENU, callback_data=AdminCb(action="menu"))
    return builder.as_markup()


def video_choice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.NC_VIDEO_YES, callback_data=NewContestCb(action="video_yes"))
    builder.button(text=texts.NC_VIDEO_NO, callback_data=NewContestCb(action="video_no"))
    builder.adjust(2)
    return builder.as_markup()


def new_contest_confirm() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.NC_SAVE, callback_data=NewContestCb(action="save"))
    builder.button(text=texts.BTN_CANCEL, callback_data=NewContestCb(action="cancel"))
    builder.adjust(1)
    return builder.as_markup()


def contests_list(contests: Sequence[Contest]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for contest in contests:
        mark = "🟢" if contest.accepting else "🔴"
        builder.button(text=f"{mark} {contest.title}", callback_data=ContestCb(action="view", id=contest.id))
    builder.button(text=texts.BTN_TO_MENU, callback_data=AdminCb(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def contest_card(contest: Contest, has_channel: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    def add(text: str, action: str) -> None:
        builder.button(text=text, callback_data=ContestCb(action=action, id=contest.id))

    if has_channel:
        add(texts.BTN_POST_CHANNEL, "post")
    add(texts.BTN_BROADCAST, "bcast")
    add(texts.BTN_PREVIEW, "preview")
    add(texts.BTN_EXCEL, "excel")
    add(texts.BTN_ZIP, "zip")
    add(texts.BTN_DEADLINE, "deadline")
    add(texts.BTN_CLOSE if contest.is_open else texts.BTN_OPEN, "toggle")
    builder.button(text=texts.BTN_TO_LIST, callback_data=AdminCb(action="list"))
    builder.adjust(1)
    return builder.as_markup()


def broadcast_confirm(contest_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_YES_SEND, callback_data=ContestCb(action="bcast_ok", id=contest_id))
    builder.button(text=texts.BTN_NO, callback_data=ContestCb(action="view", id=contest_id))
    builder.adjust(2)
    return builder.as_markup()


def review(app_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_ACCEPT, callback_data=ReviewCb(action="accepted", app_id=app_id))
    builder.button(text=texts.BTN_REJECT, callback_data=ReviewCb(action="rejected", app_id=app_id))
    builder.adjust(2)
    return builder.as_markup()
