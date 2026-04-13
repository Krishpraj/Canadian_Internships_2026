import sqlite3
from datetime import date, datetime

from config import DB_PATH
from parsers.base import Internship

_conn: sqlite3.Connection | None = None


def _get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(DB_PATH)
        _conn.execute("PRAGMA journal_mode=WAL")
    return _conn


def init_db() -> None:
    conn = _get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS seen_internships (
            uid TEXT PRIMARY KEY,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            apply_url TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            source TEXT NOT NULL,
            posted_to_discord INTEGER DEFAULT 0,
            first_seen_at TEXT NOT NULL,
            discord_posted_at TEXT
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_apply_url
        ON seen_internships(apply_url)
    """)
    conn.commit()


def is_seen(uid: str) -> bool:
    conn = _get_conn()
    row = conn.execute(
        "SELECT 1 FROM seen_internships WHERE uid = ?", (uid,)
    ).fetchone()
    return row is not None


def apply_url_exists(apply_url: str) -> bool:
    conn = _get_conn()
    row = conn.execute(
        "SELECT 1 FROM seen_internships WHERE apply_url = ?", (apply_url,)
    ).fetchone()
    return row is not None


def mark_seen(internship: Internship) -> None:
    conn = _get_conn()
    conn.execute(
        """INSERT OR IGNORE INTO seen_internships
           (uid, company, role, apply_url, date_posted, source, posted_to_discord, first_seen_at)
           VALUES (?, ?, ?, ?, ?, ?, 0, ?)""",
        (
            internship.uid,
            internship.company,
            internship.role,
            internship.apply_url,
            internship.date_posted.isoformat(),
            internship.source,
            datetime.utcnow().isoformat(),
        ),
    )
    conn.commit()


def mark_posted(uid: str) -> None:
    conn = _get_conn()
    conn.execute(
        """UPDATE seen_internships
           SET posted_to_discord = 1, discord_posted_at = ?
           WHERE uid = ?""",
        (datetime.utcnow().isoformat(), uid),
    )
    conn.commit()


def get_unsent(today: date) -> list[Internship]:
    conn = _get_conn()
    rows = conn.execute(
        """SELECT uid, company, role, '', apply_url, date_posted, source, 0
           FROM seen_internships
           WHERE posted_to_discord = 0 AND date_posted >= ?""",
        (today.isoformat(),),
    ).fetchall()
    results = []
    for r in rows:
        results.append(
            Internship(
                uid=r[0],
                company=r[1],
                role=r[2],
                location=r[3],
                apply_url=r[4],
                date_posted=date.fromisoformat(r[5]),
                source=r[6],
                is_closed=False,
            )
        )
    return results
