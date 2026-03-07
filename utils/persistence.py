"""SQLite persistence layer for auth, guardrails, journals and positions."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
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


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def _ensure_column(conn: sqlite3.Connection, table: str, column_def: str) -> None:
    col_name = column_def.split()[0]
    if col_name not in _table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_def}")


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
                    market_type TEXT NOT NULL DEFAULT 'spot',
                    pnl REAL NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            _ensure_column(conn, "journal_entries", "market_type TEXT NOT NULL DEFAULT 'spot'")
            _ensure_column(conn, "journal_entries", "pnl REAL NOT NULL DEFAULT 0")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    market_type TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    leverage REAL NOT NULL,
                    stop_loss REAL,
                    take_profit_1 REAL,
                    take_profit_2 REAL,
                    take_profit_3 REAL,
                    status TEXT NOT NULL,
                    opened_at TEXT NOT NULL,
                    closed_at TEXT,
                    close_price REAL,
                    close_reason TEXT,
                    pnl REAL
                )
                """
            )
            conn.commit()


# ----- Auth -----
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


# ----- Guardrails -----
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


# ----- Journal -----
def insert_journal_entry(
    user_id: str,
    symbol: str,
    side: str,
    thesis: str,
    emotion: str,
    result: str,
    tags: List[str],
    market_type: str,
    pnl: float,
    created_at: str,
) -> Dict:
    tags_json = json.dumps(tags, ensure_ascii=True)
    with _DB_LOCK:
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO journal_entries (user_id, symbol, side, thesis, emotion, result, tags_json, market_type, pnl, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, symbol, side, thesis, emotion, result, tags_json, market_type, pnl, created_at),
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
        "market_type": market_type,
        "pnl": float(pnl),
        "tags": tags,
        "time": created_at,
    }


def list_journal_entries(user_id: str, limit: int, market_type: Optional[str] = None) -> List[Dict]:
    safe_limit = max(1, min(limit, 200))
    with get_conn() as conn:
        if market_type:
            rows = conn.execute(
                """
                SELECT id, symbol, side, thesis, emotion, result, tags_json, market_type, pnl, created_at
                FROM journal_entries
                WHERE user_id=? AND market_type=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, market_type, safe_limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT id, symbol, side, thesis, emotion, result, tags_json, market_type, pnl, created_at
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
                "market_type": row["market_type"],
                "pnl": float(row["pnl"] or 0),
                "tags": json.loads(row["tags_json"] or "[]"),
                "time": row["created_at"],
            }
        )
    return items


def list_journal_entries_by_date(user_id: str, date_str: str) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT symbol, side, result, market_type, pnl, created_at
            FROM journal_entries
            WHERE user_id=? AND date(created_at)=date(?)
            ORDER BY id DESC
            """,
            (user_id, date_str),
        ).fetchall()
    return [dict(r) for r in rows]


# ----- Positions -----
def insert_position(
    user_id: str,
    market_type: str,
    symbol: str,
    side: str,
    entry_price: float,
    quantity: float,
    leverage: float,
    stop_loss: Optional[float],
    take_profit_1: Optional[float],
    take_profit_2: Optional[float],
    take_profit_3: Optional[float],
    opened_at: str,
) -> Dict:
    with _DB_LOCK:
        with get_conn() as conn:
            cur = conn.execute(
                """
                INSERT INTO positions (
                  user_id, market_type, symbol, side, entry_price, quantity, leverage,
                  stop_loss, take_profit_1, take_profit_2, take_profit_3,
                  status, opened_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'OPEN', ?)
                """,
                (
                    user_id,
                    market_type,
                    symbol,
                    side,
                    entry_price,
                    quantity,
                    leverage,
                    stop_loss,
                    take_profit_1,
                    take_profit_2,
                    take_profit_3,
                    opened_at,
                ),
            )
            position_id = cur.lastrowid
            conn.commit()
    return get_position(user_id, position_id)


def get_position(user_id: str, position_id: int) -> Optional[Dict]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, user_id, market_type, symbol, side, entry_price, quantity, leverage,
                   stop_loss, take_profit_1, take_profit_2, take_profit_3,
                   status, opened_at, closed_at, close_price, close_reason, pnl
            FROM positions WHERE id=? AND user_id=?
            """,
            (position_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def list_positions(user_id: str, status: str = "OPEN", market_type: Optional[str] = None) -> List[Dict]:
    query = (
        "SELECT id, market_type, symbol, side, entry_price, quantity, leverage, stop_loss, "
        "take_profit_1, take_profit_2, take_profit_3, status, opened_at, closed_at, close_price, close_reason, pnl "
        "FROM positions WHERE user_id=?"
    )
    params: List = [user_id]
    if status:
        query += " AND status=?"
        params.append(status)
    if market_type:
        query += " AND market_type=?"
        params.append(market_type)
    query += " ORDER BY id DESC LIMIT 200"

    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def update_position_risk(
    user_id: str,
    position_id: int,
    stop_loss: Optional[float],
    take_profit_1: Optional[float],
    take_profit_2: Optional[float],
    take_profit_3: Optional[float],
) -> Optional[Dict]:
    with _DB_LOCK:
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE positions
                SET stop_loss=?, take_profit_1=?, take_profit_2=?, take_profit_3=?
                WHERE id=? AND user_id=? AND status='OPEN'
                """,
                (stop_loss, take_profit_1, take_profit_2, take_profit_3, position_id, user_id),
            )
            conn.commit()
    return get_position(user_id, position_id)


def close_position(user_id: str, position_id: int, close_price: float, close_reason: str) -> Optional[Dict]:
    pos = get_position(user_id, position_id)
    if not pos or pos.get("status") != "OPEN":
        return None

    side = str(pos["side"]).upper()
    entry_price = float(pos["entry_price"])
    quantity = float(pos["quantity"])
    leverage = float(pos["leverage"])

    if side in {"BUY", "LONG"}:
        pnl = (close_price - entry_price) * quantity * leverage
    else:
        pnl = (entry_price - close_price) * quantity * leverage

    closed_at = datetime.now(timezone.utc).isoformat()
    with _DB_LOCK:
        with get_conn() as conn:
            conn.execute(
                """
                UPDATE positions
                SET status='CLOSED', closed_at=?, close_price=?, close_reason=?, pnl=?
                WHERE id=? AND user_id=? AND status='OPEN'
                """,
                (closed_at, close_price, close_reason, pnl, position_id, user_id),
            )
            conn.commit()
    return get_position(user_id, position_id)


def list_closed_positions_by_date(user_id: str, date_str: str) -> List[Dict]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT market_type, symbol, side, pnl, closed_at
            FROM positions
            WHERE user_id=? AND status='CLOSED' AND date(closed_at)=date(?)
            ORDER BY id DESC
            """,
            (user_id, date_str),
        ).fetchall()
    return [dict(r) for r in rows]
