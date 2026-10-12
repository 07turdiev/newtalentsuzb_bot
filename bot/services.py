"""E'lon yuborish, ommaviy tarqatish va adminlarga yangi ariza haqida xabar berish."""

from __future__ import annotations

import asyncio
import logging
from html import escape
from pathlib import Path

from aiogram import Bot
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message, ReplyParameters

from . import keyboards as kb
from . import texts
from .config import Config
from .db import Application, Contest, Database
from .docgen import file_name
from .forms import format_phone

log = logging.getLogger(__name__)

_background: set[asyncio.Task] = set()


async def deep_link(bot: Bot, contest_id: int) -> str:
    me = await bot.me()
    return f"https://t.me/{me.username}?start=apply_{contest_id}"


async def send_announcement(
    bot: Bot, chat_id: int | str, contest: Contest, markup: InlineKeyboardMarkup
) -> Message:
    if contest.photo_id:
        return await bot.send_photo(
            chat_id, contest.photo_id, caption=contest.announcement or None, reply_markup=markup
        )
    return await bot.send_message(chat_id, contest.announcement, reply_markup=markup)


def start_broadcast(bot: Bot, db: Database, contest: Contest, report_chat_id: int) -> None:
    task = asyncio.create_task(_broadcast(bot, db, contest, report_chat_id))
    _background.add(task)
    task.add_done_callback(_background.discard)


async def _broadcast(bot: Bot, db: Database, contest: Contest, report_chat_id: int) -> None:
    markup = kb.apply_button(contest.id)
    sent = failed = 0
    for user_id in await db.active_user_ids():
        for _attempt in range(3):
            try:
                await send_announcement(bot, user_id, contest, markup)
                sent += 1
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
                continue
            except TelegramForbiddenError:
                await db.set_user_blocked(user_id)
                failed += 1
            except Exception:
                log.exception("Broadcast to %s failed", user_id)
                failed += 1
            break
        else:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram cheklovi: sekundiga ~30 xabar

    await bot.send_message(
        report_chat_id,
        texts.BROADCAST_DONE.format(title=escape(contest.title), sent=sent, failed=failed),
    )


def _cut(value: str | None, limit: int) -> str:
    value = value or "—"
    return escape(value if len(value) <= limit else value[: limit - 1] + "…")


def admin_caption(app: Application, contest: Contest, reviewer: str | None = None) -> str:
    """Admin chatidagi ariza izohi (Telegram cheklovi 1024 belgi)."""
    d = app.data
    kind = texts.KIND_LABELS[app.kind]
    if app.kind == "team":
        kind += f" ({len(d.get('participants') or [])} nafar)"
    lines = [
        texts.NEW_APPLICATION.format(id=app.id),
        f"🏆 {_cut(contest.title, 100)}",
        kind,
        f"<b>{_cut(app.display_name, 100)}</b>",
        f"🎯 {_cut(d.get('direction'), 80)} · {_cut(d.get('age_category'), 50)}",
        f"🎼 {_cut(d.get('piece'), 150)}",
        f"📞 {format_phone(d['phone']) if d.get('phone') else '—'}",
    ]
    video = d.get("video")
    if video and video["type"] == "link":
        lines.append(f"🎬 {_cut(video['url'], 200)}")
    lines.append(f'👤 <a href="tg://user?id={app.user_id}">Yuboruvchi</a> · {app.created_at[:16]}')
    status = texts.STATUS[app.status]
    if reviewer:
        status += f" — {_cut(reviewer, 60)}"
    lines.append(f"\nHolat: {status}")
    return "\n".join(lines)


async def notify_new_application(
    bot: Bot, config: Config, app: Application, contest: Contest, doc_path: Path | None
) -> None:
    caption = admin_caption(app, contest)
    for chat_id in config.review_chats:
        try:
            if doc_path is not None:
                message = await bot.send_document(
                    chat_id,
                    FSInputFile(doc_path, filename=file_name(app.id, app.display_name)),
                    caption=caption,
                    reply_markup=kb.review(app.id),
                )
            else:
                message = await bot.send_message(chat_id, caption, reply_markup=kb.review(app.id))

            video = app.data.get("video")
            if video and video["type"] in ("video", "document"):
                send = bot.send_video if video["type"] == "video" else bot.send_document
                await send(
                    chat_id,
                    video["file_id"],
                    caption=texts.VIDEO_CAPTION.format(id=app.id),
                    reply_parameters=ReplyParameters(message_id=message.message_id),
                )
        except TelegramAPIError:
            log.exception("Could not notify chat %s about application %s", chat_id, app.id)


async def notify_user(bot: Bot, user_id: int, text: str) -> None:
    try:
        await bot.send_message(user_id, text)
    except (TelegramForbiddenError, TelegramBadRequest):
        pass
