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
from .locales import LANGS, t


class LangCb(CallbackData, prefix="lg"):
    code: str


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


class ReceiptCb(CallbackData, prefix="rc"):
    app_id: int


class AdminCb(CallbackData, prefix="ad"):
    action: str  # menu | new | list | stats | pay | pay_edit | pay_off


class NewContestCb(CallbackData, prefix="nc"):
    action: str  # video_yes | video_no | channel | broadcast | save | cancel


class ContestCb(CallbackData, prefix="ct"):
    action: str
    id: int


class ReviewCb(CallbackData, prefix="rv"):
    action: str  # accepted | unpaid | rejected
    app_id: int


def _reply(rows: list[list[KeyboardButton]]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def _btn(text: str) -> KeyboardButton:
    return KeyboardButton(text=text)


# --- ishtirokchi ---


def languages() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, name in LANGS.items():
        builder.button(text=name, callback_data=LangCb(code=code))
    builder.adjust(1)
    return builder.as_markup()


def main_menu(lang: str, is_admin: bool) -> ReplyKeyboardMarkup:
    rows = [
        [_btn(t(lang, "btn.apply"))],
        [_btn(t(lang, "btn.my_apps")), _btn(t(lang, "btn.lang"))],
    ]
    if is_admin:
        rows.append([_btn(texts.BTN_ADMIN)])
    return _reply(rows)


def cancel_only(lang: str = "uz") -> ReplyKeyboardMarkup:
    return _reply([[_btn(t(lang, "btn.cancel"))]])


def skip_cancel() -> ReplyKeyboardMarkup:
    return _reply([[_btn(texts.BTN_SKIP)], [_btn(texts.BTN_CANCEL)]])


def field_keyboard(field: Field, options: Sequence[str], can_back: bool, lang: str) -> ReplyKeyboardMarkup:
    rows: list[list[KeyboardButton]] = []
    if field.type == "choice" and options:
        per_row = 2 if all(len(o) <= 18 for o in options) else 1
        for i in range(0, len(options), per_row):
            rows.append([_btn(o) for o in options[i : i + per_row]])
    if field.type == "phone":
        rows.append([KeyboardButton(text=t(lang, "btn.phone"), request_contact=True)])
    if field.optional:
        rows.append([_btn(t(lang, "btn.skip"))])
    cancel = _btn(t(lang, "btn.cancel"))
    rows.append([_btn(t(lang, "btn.back")), cancel] if can_back else [cancel])
    return _reply(rows)


def apply_button(contest_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(
            text=t(lang, "btn.apply"), callback_data=ApplyCb(contest_id=contest_id).pack()
        )]]
    )


def channel_buttons(apply_url: str, bot_url: str) -> InlineKeyboardMarkup:
    """Kanal posti ostidagi tugmalar: ariza yuborish va botga havola."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t("uz", "btn.apply"), url=apply_url)],
        [InlineKeyboardButton(text=texts.BTN_OPEN_BOT, url=bot_url)],
    ])


def contests_choice(contests: Sequence[Contest]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for contest in contests:
        builder.button(text=contest.title, callback_data=ApplyCb(contest_id=contest.id))
    builder.adjust(1)
    return builder.as_markup()


def kind_choice(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for kind in ("solo", "team"):
        builder.button(text=t(lang, f"kind.{kind}"), callback_data=KindCb(kind=kind))
    builder.adjust(1)
    return builder.as_markup()


def confirm(lang: str, with_payment: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=t(lang, "btn.confirm_pay" if with_payment else "btn.confirm"),
        callback_data=ConfirmCb(action="send"),
    )
    builder.button(text=t(lang, "btn.edit"), callback_data=ConfirmCb(action="edit"))
    builder.button(text=t(lang, "btn.cancel"), callback_data=ConfirmCb(action="cancel"))
    builder.adjust(1, 2)
    return builder.as_markup()


def edit_fields(fields: Sequence[Field], lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for index, field in enumerate(fields):
        builder.button(text=field.label(lang), callback_data=EditCb(index=index))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text=t(lang, "btn.back"), callback_data=ConfirmCb(action="back").pack()))
    return builder.as_markup()


def my_apps(apps: Sequence[Application], lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for app in apps:
        if app.status in ("awaiting_payment", "unpaid"):
            builder.row(InlineKeyboardButton(
                text=t(lang, "btn.receipt", id=app.id),
                callback_data=ReceiptCb(app_id=app.id).pack(),
            ))
    docs = [
        InlineKeyboardButton(text=f"📄 №{app.id}", callback_data=MyDocCb(app_id=app.id).pack())
        for app in apps
        if app.doc_path
    ]
    for i in range(0, len(docs), 4):
        builder.row(*docs[i : i + 4])
    return builder.as_markup()


def receipt_again(app_id: int, lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(
        text=t(lang, "btn.receipt_again"), callback_data=ReceiptCb(app_id=app_id).pack()
    )]])


# --- admin ---


def admin_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_NEW_CONTEST, callback_data=AdminCb(action="new"))
    builder.button(text=texts.BTN_CONTEST_LIST, callback_data=AdminCb(action="list"))
    builder.button(text=texts.BTN_PAYMENT, callback_data=AdminCb(action="pay"))
    builder.button(text=texts.BTN_STATS, callback_data=AdminCb(action="stats"))
    builder.adjust(1)
    return builder.as_markup()


def back_to_admin() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_TO_MENU, callback_data=AdminCb(action="menu"))
    return builder.as_markup()


def payment_settings(enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_PAYMENT_EDIT, callback_data=AdminCb(action="pay_edit"))
    if enabled:
        builder.button(text=texts.BTN_PAYMENT_OFF, callback_data=AdminCb(action="pay_off"))
    builder.button(text=texts.BTN_TO_MENU, callback_data=AdminCb(action="menu"))
    builder.adjust(1)
    return builder.as_markup()


def video_choice() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.NC_VIDEO_YES, callback_data=NewContestCb(action="video_yes"))
    builder.button(text=texts.NC_VIDEO_NO, callback_data=NewContestCb(action="video_no"))
    builder.adjust(2)
    return builder.as_markup()


def new_contest_publish(to_channel: bool, to_users: bool) -> InlineKeyboardMarkup:
    """E'lon qayerga yuborilishini belgilash (checkbox ko'rinishida) va saqlash."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text=("☑️ " if to_channel else "⬜️ ") + texts.NC_TOGGLE_CHANNEL,
        callback_data=NewContestCb(action="channel"),
    )
    builder.button(
        text=("☑️ " if to_users else "⬜️ ") + texts.NC_TOGGLE_BROADCAST,
        callback_data=NewContestCb(action="broadcast"),
    )
    builder.button(
        text=texts.NC_SAVE_PUBLISH if to_channel or to_users else texts.NC_SAVE_ONLY,
        callback_data=NewContestCb(action="save"),
    )
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


def review(app_id: int, with_payment: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=texts.BTN_ACCEPT, callback_data=ReviewCb(action="accepted", app_id=app_id))
    if with_payment:
        builder.button(text=texts.BTN_UNPAID, callback_data=ReviewCb(action="unpaid", app_id=app_id))
    builder.button(text=texts.BTN_REJECT, callback_data=ReviewCb(action="rejected", app_id=app_id))
    builder.adjust(1)
    return builder.as_markup()
