"""User guardrails and journaling helpers with SQLite persistence."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List

from utils.persistence import (
    init_db,
    get_guardrail_settings,
    upsert_guardrail_settings,
    get_guardrail_state,
    upsert_guardrail_state,
    insert_journal_entry,
    list_journal_entries,
)

init_db()


def _today_key(now: datetime) -> str:
    return now.strftime("%Y-%m-%d")


def get_user_guardrail_config(user_id: str) -> Dict:
    return get_guardrail_settings(user_id)


def update_user_guardrail_config(
    user_id: str,
    max_trades_per_day: int,
    cooldown_losses: int,
    cooldown_minutes: int,
) -> Dict:
    if max_trades_per_day <= 0:
        raise ValueError("max_trades_per_day must be > 0")
    if cooldown_losses <= 0:
        raise ValueError("cooldown_losses must be > 0")
    if cooldown_minutes <= 0:
        raise ValueError("cooldown_minutes must be > 0")

    now = datetime.now(timezone.utc).isoformat()
    return upsert_guardrail_settings(
        user_id=user_id,
        max_trades_per_day=max_trades_per_day,
        cooldown_losses=cooldown_losses,
        cooldown_minutes=cooldown_minutes,
        updated_at=now,
    )


def evaluate_guardrail(user_id: str, outcome: str) -> Dict:
    """Track streak/day activity and return whether user should be paused."""
    now = datetime.now(timezone.utc)
    today = _today_key(now)
    config = get_guardrail_settings(user_id)

    state = get_guardrail_state(user_id) or {
        "date": today,
        "trades_today": 0,
        "losing_streak": 0,
        "cooldown_until": None,
    }

    if state["date"] != today:
        state["date"] = today
        state["trades_today"] = 0
        state["losing_streak"] = 0
        state["cooldown_until"] = None

    state["trades_today"] += 1

    outcome = (outcome or "").strip().lower()
    if outcome in {"loss", "lose", "亏损", "-"}:
        state["losing_streak"] += 1
    elif outcome in {"win", "profit", "盈利", "+"}:
        state["losing_streak"] = 0

    should_block = False
    reasons: List[str] = []

    cooldown_until = None
    if state.get("cooldown_until"):
        try:
            cooldown_until = datetime.fromisoformat(state["cooldown_until"])
        except ValueError:
            cooldown_until = None

    if cooldown_until and now < cooldown_until:
        should_block = True
        reasons.append("冷静期尚未结束")

    if state["trades_today"] > config["max_trades_per_day"]:
        should_block = True
        reasons.append(f"超过日内交易上限({config['max_trades_per_day']})")

    if state["losing_streak"] >= config["cooldown_losses"]:
        cooldown_until = now + timedelta(minutes=config["cooldown_minutes"])
        state["cooldown_until"] = cooldown_until.isoformat()
        should_block = True
        reasons.append(f"连续亏损达到{config['cooldown_losses']}笔，触发冷静期")

    upsert_guardrail_state(
        user_id=user_id,
        date=state["date"],
        trades_today=int(state["trades_today"]),
        losing_streak=int(state["losing_streak"]),
        cooldown_until=state.get("cooldown_until"),
    )

    return {
        "user_id": user_id,
        "config": config,
        "trades_today": state["trades_today"],
        "losing_streak": state["losing_streak"],
        "should_block": should_block,
        "cooldown_until": state.get("cooldown_until"),
        "reason": "；".join(reasons) if reasons else "允许继续交易",
    }


def calculate_position_size(
    account_size: float,
    risk_pct: float,
    entry_price: float,
    stop_price: float,
    leverage: float = 1.0,
) -> Dict:
    """Risk-based position sizing helper."""
    if account_size <= 0:
        raise ValueError("account_size must be > 0")
    if risk_pct <= 0:
        raise ValueError("risk_pct must be > 0")
    if entry_price <= 0 or stop_price <= 0:
        raise ValueError("entry/stop must be > 0")
    if entry_price == stop_price:
        raise ValueError("entry_price and stop_price cannot be equal")
    if leverage <= 0:
        raise ValueError("leverage must be > 0")

    risk_amount = account_size * (risk_pct / 100.0)
    stop_distance = abs(entry_price - stop_price)
    quantity = risk_amount / stop_distance
    notional = quantity * entry_price
    margin_required = notional / leverage

    return {
        "risk_amount": round(risk_amount, 2),
        "stop_distance": round(stop_distance, 6),
        "quantity": round(quantity, 6),
        "notional": round(notional, 2),
        "margin_required": round(margin_required, 2),
    }


def add_journal_entry(user_id: str, entry: Dict) -> Dict:
    """Persist one journal item and return saved payload."""
    payload = {
        "symbol": entry.get("symbol", "BTCUSDT").upper(),
        "side": entry.get("side", "BUY").upper(),
        "thesis": entry.get("thesis", ""),
        "emotion": entry.get("emotion", "neutral"),
        "result": entry.get("result", "open"),
        "tags": entry.get("tags", []),
    }
    now = datetime.now(timezone.utc).isoformat()
    return insert_journal_entry(
        user_id=user_id,
        symbol=payload["symbol"],
        side=payload["side"],
        thesis=payload["thesis"],
        emotion=payload["emotion"],
        result=payload["result"],
        tags=payload["tags"],
        created_at=now,
    )


def list_journal(user_id: str, limit: int = 30) -> List[Dict]:
    """Get latest journal entries by user."""
    return list_journal_entries(user_id=user_id, limit=limit)
