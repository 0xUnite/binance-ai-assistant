"""Entry suggestion and TP/SL helper for spot, futures and onchain markets."""
from __future__ import annotations

from typing import Dict

from indicators.indicators import analyze_market
from utils.binance_api import get_24h_ticker, get_klines


def _normalize_symbol(symbol: str) -> str:
    s = symbol.upper().strip()
    return s if s.endswith("USDT") else f"{s}USDT"


def _market_side(side: str) -> str:
    side = (side or "LONG").upper()
    if side in {"BUY", "LONG"}:
        return "LONG"
    return "SHORT"


def _avg_range_pct(klines: list[dict], lookback: int = 20) -> float:
    sample = klines[-lookback:] if len(klines) >= lookback else klines
    if not sample:
        return 0.015
    ranges = []
    for k in sample:
        close = max(float(k["close"]), 1e-9)
        ranges.append((float(k["high"]) - float(k["low"])) / close)
    return sum(ranges) / len(ranges)


def build_entry_suggestion(symbol: str, market_type: str = "spot", side: str = "LONG") -> Dict:
    """Return one actionable entry suggestion and whether opening is allowed now."""
    pair = _normalize_symbol(symbol)
    market = (market_type or "spot").lower()
    side_norm = _market_side(side)

    ticker = get_24h_ticker(pair)
    klines = get_klines(pair, "1h", 120)
    prices = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    analysis = analyze_market(prices, volumes)

    current = float(ticker["price"])
    volatility = max(_avg_range_pct(klines), 0.005)

    allow = True
    reasons = []
    score = 50

    if market == "spot" and side_norm == "SHORT":
        allow = False
        reasons.append("现货模式不建议做空")
        score -= 25

    if side_norm == "LONG":
        if analysis.get("signal") == "买入":
            score += 20
            reasons.append("指标给出买入信号")
        if analysis.get("trend") == "上涨":
            score += 15
            reasons.append("趋势向上")
        if float(analysis.get("rsi", 50)) > 72:
            score -= 20
            reasons.append("RSI偏高，追高风险")
    else:
        if analysis.get("signal") == "卖出":
            score += 20
            reasons.append("指标给出卖出信号")
        if analysis.get("trend") == "下跌":
            score += 15
            reasons.append("趋势向下")
        if float(analysis.get("rsi", 50)) < 28:
            score -= 20
            reasons.append("RSI偏低，追空风险")

    if score < 55:
        allow = False
        reasons.append("综合评分不足，建议等待")

    risk_distance = current * (volatility * 1.35)
    if side_norm == "LONG":
        entry_low = current * (1 - volatility * 0.3)
        entry_high = current * (1 + volatility * 0.25)
        stop_loss = current - risk_distance
        tp1 = current + risk_distance * 1.0
        tp2 = current + risk_distance * 1.8
        tp3 = current + risk_distance * 2.8
    else:
        entry_low = current * (1 - volatility * 0.25)
        entry_high = current * (1 + volatility * 0.3)
        stop_loss = current + risk_distance
        tp1 = current - risk_distance * 1.0
        tp2 = current - risk_distance * 1.8
        tp3 = current - risk_distance * 2.8

    leverage = 1
    if market == "futures":
        leverage = 2 if volatility > 0.03 else 3 if volatility > 0.02 else 4

    return {
        "symbol": pair,
        "market_type": market,
        "side": side_norm,
        "allow_open": allow,
        "confidence": max(0, min(int(score), 100)),
        "reasons": reasons,
        "ticker": {
            "price": current,
            "change_24h": float(ticker.get("change_24h", 0)),
        },
        "analysis": {
            "signal": analysis.get("signal"),
            "trend": analysis.get("trend"),
            "rsi": analysis.get("rsi"),
        },
        "entry_zone": {
            "low": round(entry_low, 6),
            "high": round(entry_high, 6),
        },
        "risk_plan": {
            "stop_loss": round(stop_loss, 6),
            "take_profit_1": round(tp1, 6),
            "take_profit_2": round(tp2, 6),
            "take_profit_3": round(tp3, 6),
            "suggested_leverage": leverage,
        },
        "note": "仅供参考，不构成投资建议",
    }
