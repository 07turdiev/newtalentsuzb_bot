from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import aiosqlite

from .config import now

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    full_name   TEXT,
    username    TEXT,
    lang        TEXT,                   -- uz | ru | en (tanlanmagan bo'lsa NULL)
    blocked     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    announcement    TEXT NOT NULL DEFAULT '',
    photo_id        TEXT,
    deadline        TEXT,               -- YYYY-MM-DD, shu kun ham kiradi
    directions      TEXT NOT NULL DEFAULT '[]',
    age_categories  TEXT NOT NULL DEFAULT '[]',
    require_video   INTEGER NOT NULL DEFAULT 0,
    is_open         INTEGER NOT NULL DEFAULT 1,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS applications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id  INTEGER NOT NULL REFERENCES contests(id),
    user_id     INTEGER NOT NULL,
    kind        TEXT NOT NULL,          -- solo | team
    data        TEXT NOT NULL,          -- JSON: anketa javoblari
    -- awaiting_payment | new | unpaid | accepted | rejected
    status      TEXT NOT NULL DEFAULT 'new',
    doc_path    TEXT,                   -- data/ papkasiga nisbatan yo'l
    receipt     TEXT,                   -- JSON: to'lov cheki (type, file_id, at)
    created_at  TEXT NOT NULL
);

-- Botdan qo'shilgan adminlar (.env dagi ADMIN_IDS dan tashqari)
CREATE TABLE IF NOT EXISTS admins (
    id          INTEGER PRIMARY KEY,    -- Telegram ID
    name        TEXT,
    added_by    INTEGER,
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_applications_contest ON applications(contest_id);
CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);
"""

# Eski bazaga keyin qo'shilgan ustunlar: (jadval, ustun, turi)
MIGRATIONS = (
    ("users", "lang", "TEXT"),
    ("applications", "receipt", "TEXT"),
)


def _timestamp() -> str:
    return now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Contest:
    id: int
    title: str
    announcement: str
    photo_id: str | None
    deadline: date | None
    directions: list[str]
    age_categories: list[str]
    require_video: bool
    is_open: bool
    created_at: str

    @property
    def accepting(self) -> bool:
        """Ariza qabul qilinyaptimi: ochiq va muddati o'tmagan."""
        if not self.is_open:
            return False
        return self.deadline is None or now().date() <= self.deadline

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> Contest:
        return cls(
            id=row["id"],
            title=row["title"],
            announcement=row["announcement"],
            photo_id=row["photo_id"],
            deadline=date.fromisoformat(row["deadline"]) if row["deadline"] else None,
            directions=json.loads(row["directions"]),
            age_categories=json.loads(row["age_categories"]),
            require_video=bool(row["require_video"]),
            is_open=bool(row["is_open"]),
            created_at=row["created_at"],
        )


@dataclass
class Application:
    id: int
    contest_id: int
    user_id: int
    kind: str
    data: dict[str, Any]
    status: str
    doc_path: str | None
    created_at: str
    receipt: dict[str, str] | None = None
    contest_title: str = field(default="")

    @property
    def display_name(self) -> str:
        return self.data.get("full_name") or self.data.get("team_name") or "—"

    @classmethod
    def from_row(cls, row: aiosqlite.Row) -> Application:
        keys = row.keys()
        return cls(
            id=row["id"],
            contest_id=row["contest_id"],
            user_id=row["user_id"],
            kind=row["kind"],
            data=json.loads(row["data"]),
            status=row["status"],
            doc_path=row["doc_path"],
            created_at=row["created_at"],
            receipt=json.loads(row["receipt"]) if row["receipt"] else None,
            contest_title=row["contest_title"] if "contest_title" in keys else "",
        )


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._conn: aiosqlite.Connection | None = None
        self._langs: dict[int, str | None] = {}
        self.admin_ids: frozenset[int] = frozenset()  # botdan qo'shilgan adminlar

    @property
    def conn(self) -> aiosqlite.Connection:
        if self._conn is None:
            raise RuntimeError("Database.connect() chaqirilmagan")
        return self._conn

    async def connect(self) -> None:
        self._conn = await aiosqlite.connect(self.path)
        self._conn.row_factory = aiosqlite.Row
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.execute("PRAGMA foreign_keys=ON")
        await self._conn.executescript(SCHEMA)
        for table, column, kind in MIGRATIONS:
            async with self._conn.execute(f"PRAGMA table_info({table})") as cur:
                columns = {row["name"] for row in await cur.fetchall()}
            if column not in columns:
                await self._conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {kind}")
        await self._conn.commit()
        await self._load_admins()

    async def close(self) -> None:
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def _fetchone(self, sql: str, params: tuple = ()) -> aiosqlite.Row | None:
        async with self.conn.execute(sql, params) as cur:
            return await cur.fetchone()

    async def _fetchall(self, sql: str, params: tuple = ()) -> list[aiosqlite.Row]:
        async with self.conn.execute(sql, params) as cur:
            return list(await cur.fetchall())

    # --- foydalanuvchilar ---

    async def upsert_user(self, user_id: int, full_name: str, username: str | None) -> None:
        await self.conn.execute(
            """
            INSERT INTO users (id, full_name, username, created_at) VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                full_name = excluded.full_name, username = excluded.username, blocked = 0
            """,
            (user_id, full_name, username, _timestamp()),
        )
        await self.conn.commit()

    async def set_user_blocked(self, user_id: int, blocked: bool = True) -> None:
        await self.conn.execute("UPDATE users SET blocked = ? WHERE id = ?", (int(blocked), user_id))
        await self.conn.commit()

    async def get_lang(self, user_id: int) -> str | None:
        """Foydalanuvchi tanlagan til yoki None (hali tanlamagan)."""
        if user_id not in self._langs:
            row = await self._fetchone("SELECT lang FROM users WHERE id = ?", (user_id,))
            self._langs[user_id] = row["lang"] if row else None
        return self._langs[user_id]

    async def set_lang(self, user_id: int, lang: str) -> None:
        await self.conn.execute("UPDATE users SET lang = ? WHERE id = ?", (lang, user_id))
        await self.conn.commit()
        self._langs[user_id] = lang

    async def active_users(self) -> list[tuple[int, str | None]]:
        rows = await self._fetchall("SELECT id, lang FROM users WHERE blocked = 0 ORDER BY id")
        return [(row["id"], row["lang"]) for row in rows]

    async def user_counts(self) -> tuple[int, int]:
        row = await self._fetchone("SELECT COUNT(*) AS total, TOTAL(blocked = 0) AS active FROM users")
        return row["total"], int(row["active"])

    # --- tanlovlar ---

    async def create_contest(
        self,
        title: str,
        announcement: str,
        photo_id: str | None,
        deadline: date | None,
        directions: list[str],
        age_categories: list[str],
        require_video: bool,
    ) -> int:
        cur = await self.conn.execute(
            """
            INSERT INTO contests
                (title, announcement, photo_id, deadline, directions, age_categories,
                 require_video, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title,
                announcement,
                photo_id,
                deadline.isoformat() if deadline else None,
                json.dumps(directions, ensure_ascii=False),
                json.dumps(age_categories, ensure_ascii=False),
                int(require_video),
                _timestamp(),
            ),
        )
        await self.conn.commit()
        return cur.lastrowid

    async def get_contest(self, contest_id: int) -> Contest | None:
        row = await self._fetchone("SELECT * FROM contests WHERE id = ?", (contest_id,))
        return Contest.from_row(row) if row else None

    async def list_contests(self, limit: int = 30) -> list[Contest]:
        rows = await self._fetchall("SELECT * FROM contests ORDER BY id DESC LIMIT ?", (limit,))
        return [Contest.from_row(row) for row in rows]

    async def accepting_contests(self) -> list[Contest]:
        rows = await self._fetchall("SELECT * FROM contests WHERE is_open = 1 ORDER BY id")
        return [c for c in map(Contest.from_row, rows) if c.accepting]

    async def set_contest_open(self, contest_id: int, is_open: bool) -> None:
        await self.conn.execute(
            "UPDATE contests SET is_open = ? WHERE id = ?", (int(is_open), contest_id)
        )
        await self.conn.commit()

    async def set_contest_deadline(self, contest_id: int, deadline: date | None) -> None:
        await self.conn.execute(
            "UPDATE contests SET deadline = ? WHERE id = ?",
            (deadline.isoformat() if deadline else None, contest_id),
        )
        await self.conn.commit()

    async def contest_stats(self, contest_id: int) -> dict[str, int]:
        row = await self._fetchone(
            """
            SELECT COUNT(*) AS total,
                   TOTAL(kind = 'solo') AS solo,
                   TOTAL(kind = 'team') AS team,
                   TOTAL(status = 'awaiting_payment') AS awaiting_payment,
                   TOTAL(status = 'new') AS new,
                   TOTAL(status = 'unpaid') AS unpaid,
                   TOTAL(status = 'accepted') AS accepted,
                   TOTAL(status = 'rejected') AS rejected
            FROM applications WHERE contest_id = ?
            """,
            (contest_id,),
        )
        return {key: int(row[key]) for key in row.keys()}

    # --- arizalar ---

    async def create_application(
        self, contest_id: int, user_id: int, kind: str, data: dict[str, Any], status: str = "new"
    ) -> Application:
        cur = await self.conn.execute(
            """
            INSERT INTO applications (contest_id, user_id, kind, data, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (contest_id, user_id, kind, json.dumps(data, ensure_ascii=False), status, _timestamp()),
        )
        await self.conn.commit()
        app = await self.get_application(cur.lastrowid)
        assert app is not None
        return app

    async def set_application_doc(self, app_id: int, doc_path: str) -> None:
        await self.conn.execute("UPDATE applications SET doc_path = ? WHERE id = ?", (doc_path, app_id))
        await self.conn.commit()

    async def set_application_status(self, app_id: int, status: str) -> None:
        await self.conn.execute("UPDATE applications SET status = ? WHERE id = ?", (status, app_id))
        await self.conn.commit()

    async def set_receipt(self, app_id: int, receipt: dict[str, str]) -> None:
        """To'lov chekini saqlaydi va arizani ko'rib chiqishga yuboradi."""
        receipt = {**receipt, "at": _timestamp()}
        await self.conn.execute(
            "UPDATE applications SET receipt = ?, status = 'new' WHERE id = ?",
            (json.dumps(receipt, ensure_ascii=False), app_id),
        )
        await self.conn.commit()

    async def get_application(self, app_id: int) -> Application | None:
        row = await self._fetchone(
            """
            SELECT a.*, c.title AS contest_title
            FROM applications a JOIN contests c ON c.id = a.contest_id
            WHERE a.id = ?
            """,
            (app_id,),
        )
        return Application.from_row(row) if row else None

    async def user_applications(self, user_id: int, limit: int = 20) -> list[Application]:
        rows = await self._fetchall(
            """
            SELECT a.*, c.title AS contest_title
            FROM applications a JOIN contests c ON c.id = a.contest_id
            WHERE a.user_id = ? ORDER BY a.id DESC LIMIT ?
            """,
            (user_id, limit),
        )
        return [Application.from_row(row) for row in rows]

    async def contest_applications(self, contest_id: int) -> list[Application]:
        rows = await self._fetchall(
            """
            SELECT a.*, c.title AS contest_title
            FROM applications a JOIN contests c ON c.id = a.contest_id
            WHERE a.contest_id = ? ORDER BY a.id
            """,
            (contest_id,),
        )
        return [Application.from_row(row) for row in rows]

    # --- botdan qo'shilgan adminlar ---

    async def _load_admins(self) -> None:
        rows = await self._fetchall("SELECT id FROM admins")
        self.admin_ids = frozenset(row["id"] for row in rows)

    async def list_admins(self) -> list[tuple[int, str | None]]:
        """(id, ism) ro'yxati: foydalanuvchining botdagi joriy ismi yoki qo'shilgandagi ismi."""
        rows = await self._fetchall(
            "SELECT a.id, COALESCE(u.full_name, a.name) AS name "
            "FROM admins a LEFT JOIN users u ON u.id = a.id ORDER BY a.created_at"
        )
        return [(row["id"], row["name"]) for row in rows]

    async def add_admin(self, user_id: int, name: str | None, added_by: int) -> None:
        await self.conn.execute(
            "INSERT OR REPLACE INTO admins (id, name, added_by, created_at) VALUES (?, ?, ?, ?)",
            (user_id, name, added_by, _timestamp()),
        )
        await self.conn.commit()
        await self._load_admins()

    async def remove_admin(self, user_id: int) -> None:
        await self.conn.execute("DELETE FROM admins WHERE id = ?", (user_id,))
        await self.conn.commit()
        await self._load_admins()

    async def user_name(self, user_id: int) -> str | None:
        row = await self._fetchone("SELECT full_name FROM users WHERE id = ?", (user_id,))
        return row["full_name"] if row else None

    async def total_applications(self) -> int:
        row = await self._fetchone("SELECT COUNT(*) AS n FROM applications")
        return row["n"]

    # --- sozlamalar ---

    async def get_setting(self, key: str) -> Any:
        row = await self._fetchone("SELECT value FROM settings WHERE key = ?", (key,))
        return json.loads(row["value"]) if row else None

    async def set_setting(self, key: str, value: Any) -> None:
        await self.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, json.dumps(value, ensure_ascii=False)),
        )
        await self.conn.commit()

    async def delete_setting(self, key: str) -> None:
        await self.conn.execute("DELETE FROM settings WHERE key = ?", (key,))
        await self.conn.commit()

    async def get_payment(self) -> dict[str, str] | None:
        """To'lov rekvizitlari: {"card", "holder", "amount"}. None — to'lov o'chirilgan."""
        payment = await self.get_setting("payment")
        return payment if payment and payment.get("card") else None
