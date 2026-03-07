"""SQLite persistence layer for auth, guardrails and journal."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Dict, List, Optional

DB_PATH = os.getenv("BINANCE_ASSISTANT_DB", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "assistant.db"))
_DB_LOCK = threading.Lock()


def _ensure_db_dir() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


@contextmanager
def get_conn():
    _ensure_db_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with _DB_LOCK:
        with get_conn() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS guardrail_settings (
                    user_id TEXT PRIMARY KEY,
                    max_trades_per_day INTEGER NOT NULL,
                    cooldown_losses INTEGER NOT NULL,
                    cooldown_minutes INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS guardrail_state (
                    user_id TEXT PRIMARY KEY,
                    date TEXT NOT NULL,
                    trades_today INTEGER NOT NULL,
                    losing_streak INTEGER NOT NULL,
                    cooldown_until TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    thesis TEXT,
                    emotion TEXT,
                    result TEXT,
                    tags_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()


def create_user(username: str, password_hash: str, created_at: str) -> bool:
    with _DB_LOCK:
        with get_conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                    (username, password_hash, created_at),
                )
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False


def get_user(username: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT username, password_hash, created_at FROM users WHERE username=?", (username,)).fetchone()
        return dict(row) if row else None


def get_guardrail_settings(user_id: str) -> Dict:
    defaults = {"max_trades_per_day": 8, "cooldown_losses": 3, "cooldown_minutes": 45}
    with get_conn() as conn:
        row = conn.execute(
            "SELECT max_trades_per_day, cooldown_losses, cooldown_minutes FROM guardrail_settings WHERE user_id=?",
            (user_id,),
        ).fetchone()
        if not row:
            return defaults
        return {
            "max_trades_per_day": int(row["max_trades_per_day"]),
            "cooldown_losses": int(row["cooldown_losses"]),
            "cooldown_minutes": int(row["cooldown_minutes"]),
        }


def upsert_guardrail_settings(user_id: str, max_trades_per_day: int, cooldown_losses: int, cooldown_minutes: int, updated_at: str) -> Dict:
    with _DB_LOCK:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO guardrail_settings (user_id, max_trades_per_day, cooldown_losses, cooldown_minutes, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                max_trades_per_day=excluded.max_trades_per_day,
                cooldown_losses=excluded.cooldown_losses,
                cooldown_minutes=excluded.cooldown_minutes,
                updated_at=excluded.updated_at
                """,
                (user_id, max_trades_per_day, cooldown_losses, cooldown_minutes, updated_at),
            )
            conn.commit()
    return get_guardrail_settings(user_id)


def get_guardrail_state(user_id: str) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT date, trades_today, losing_streak, cooldown_until FROM guardrail_state WHERE user_id=?",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def upsert_guardrail_state(user_id: str, date: str, trades_today: int, losing_streak: int, cooldown_until: Optional[str]) -> None:
    with _DB_LOCK:
        with get_conn() as conn:
            conn.execute(
                """
                INSERT INTO guardrail_state (user_id, date, trades_today, losing_streak, cooldown_until)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                date=excluded.date,
                trades_today=excluded.trades_today,
                losing_streak=excluded.losing_streak,
                cooldown_until=excluded.cooldown_until
                """,
                (user_id, date, trades_today, losing_streak, cooldown_until),
            )
            conn.commit()


def insert_journal_entry(user_id: str, symbol: str, side: str, thesis: str, emotion: str, result: str, tags: List[str], created_at: str) -> Dict:
    tags_json = json.dumps(tags, ensure_ascii=True)
    with _DB_LOCK:
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO journal_entries (user_id, symbol, side, thesis, emotion, result, tags_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, symbol, side, thesis, emotion, result, tags_json, created_at),
            )
            entry_id = cur.lastrowid
            conn.commit()
    return {
        "id": entry_id,
        "user_id": user_id,
        "symbol": symbol,
        "side": side,
        "thesis": thesis,
        "emotion": emotion,
        "result": result,
        "tags": tags,
        "time": created_at,
    }


def list_journal_entries(user_id: str, limit: int) -> List[Dict]:
    safe_limit = max(1, min(limit, 200))
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, symbol, side, thesis, emotion, result, tags_json, created_at
            FROM journal_entries
            WHERE user_id=?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, safe_limit),
        ).fetchall()

    items = []
    for row in rows:
        items.append(
            {
                "id": row["id"],
                "symbol": row["symbol"],
                "side": row["side"],
                "thesis": row["thesis"],
                "emotion": row["emotion"],
                "result": row["result"],
                "tags": json.loads(row["tags_json"] or "[]"),
                "time": row["created_at"],
            }
        )
    return items
