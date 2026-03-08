"""DumpDetective integration based on Binance Web3 public endpoints."""
from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional

import requests

BASE = "https://web3.binance.com"
TIMEOUT = 12

CHAIN_MAP = {
    "bsc": "56",
    "base": "8453",
    "solana": "CT_501",
}


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _request_json(method: str, url: str, params: Optional[dict] = None, payload: Optional[dict] = None, headers: Optional[dict] = None) -> dict:
    if method == "GET":
        resp = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
    else:
        resp = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    data = resp.json()
    return data


def _step_audit(chain_id: str, contract_address: str) -> Dict:
    url = f"{BASE}/bapi/defi/v1/public/wallet-direct/security/token/audit"
    payload = {
        "binanceChainId": chain_id,
        "contractAddress": contract_address,
        "requestId": str(uuid.uuid4()),
    }
    data = _request_json("POST", url, payload=payload)
    body = data.get("data") or {}
    risk_items = body.get("riskItems") or []
    return {
        "risk_level": body.get("riskLevel", 0),
        "risk_level_enum": body.get("riskLevelEnum", "UNKNOWN"),
        "buy_tax": _safe_float((body.get("extraInfo") or {}).get("buyTax"), 0),
        "sell_tax": _safe_float((body.get("extraInfo") or {}).get("sellTax"), 0),
        "high_risk_count": sum(1 for item in risk_items if str(item.get("riskLevel", "")).upper() == "HIGH"),
        "raw": body,
    }


def _step_market_dynamic(chain_id: str, contract_address: str) -> Dict:
    url = f"{BASE}/bapi/defi/v4/public/wallet-direct/buw/wallet/market/token/dynamic/info"
    params = {"chainId": chain_id, "contractAddress": contract_address}
    data = _request_json("GET", url, params=params)
    body = data.get("data") or {}

    buy_24h = _safe_float(body.get("volume24hBuy"))
    sell_24h = _safe_float(body.get("volume24hSell"))
    total_24h = max(buy_24h + sell_24h, 1e-9)
    sell_ratio = sell_24h / total_24h

    return {
        "price": _safe_float(body.get("price")),
        "market_cap": _safe_float(body.get("marketCap")),
        "fdv": _safe_float(body.get("fdv")),
        "buy_24h_usd": buy_24h,
        "sell_24h_usd": sell_24h,
        "sell_ratio": sell_ratio,
        "smart_money_holders": int(_safe_float(body.get("smartMoneyHolders"), 0)),
        "dev_holding_percent": _safe_float(body.get("devHoldingPercent"), 0),
        "holders": int(_safe_float(body.get("holders"), 0)),
        "percent_change_24h": _safe_float(body.get("percentChange24h"), 0),
        "volume_1h": _safe_float(body.get("volume1h"), 0),
        "volume_24h": _safe_float(body.get("volume24h"), 0),
        "raw": body,
    }


def _step_smart_money(chain_id: str, contract_address: str) -> Dict:
    url = f"{BASE}/bapi/defi/v1/public/wallet-direct/buw/wallet/web/signal/smart-money"
    payload = {"chainId": chain_id, "page": 1, "pageSize": 100}
    data = _request_json("POST", url, payload=payload)
    rows = data.get("data") or []
    contract_l = contract_address.lower()
    matched = [r for r in rows if str(r.get("contractAddress", "")).lower() == contract_l]
    return {
        "in_smart_money_board": len(matched) > 0,
        "matched_signals": matched[:5],
    }


def _step_hype_proxy(dynamic: Dict) -> Dict:
    """Endpoint for social rank is unstable; use low-friction proxy from activity + price/volume trend."""
    vol_1h = dynamic.get("volume_1h", 0)
    vol_24h = max(dynamic.get("volume_24h", 0), 1e-9)
    ratio = vol_1h / vol_24h
    change_24h = dynamic.get("percent_change_24h", 0)

    hot = ratio > 0.12 or change_24h > 8
    fading = ratio < 0.03 and change_24h < 0

    if hot:
        state = "HOT"
    elif fading:
        state = "FADING"
    else:
        state = "NEUTRAL"

    return {
        "state": state,
        "volume_1h_to_24h": ratio,
        "change_24h": change_24h,
        "note": "基于交易活跃度与24h涨跌的热度代理模型",
    }


def _step_creator_wallet(chain_id: str, creator_address: Optional[str]) -> Dict:
    if not creator_address:
        return {
            "checked": False,
            "available": False,
            "has_active_positions": None,
            "reason": "未提供 creator 地址，跳过该步",
        }

    url = f"{BASE}/bapi/defi/v3/public/wallet-direct/buw/wallet/address/pnl/active-position-list"
    params = {"address": creator_address, "chainId": chain_id}
    headers = {"clienttype": "web", "clientversion": "1.2.0"}

    try:
        data = _request_json("GET", url, params=params, headers=headers)
    except Exception as e:
        return {
            "checked": True,
            "available": False,
            "has_active_positions": None,
            "reason": f"creator 接口不可用: {e}",
        }

    code = str(data.get("code", ""))
    if code != "000000":
        return {
            "checked": True,
            "available": False,
            "has_active_positions": None,
            "reason": f"creator 接口返回 {code}: {data.get('message')}",
        }

    rows = data.get("data") or []
    has_positions = len(rows) > 0
    return {
        "checked": True,
        "available": True,
        "has_active_positions": has_positions,
        "positions_count": len(rows),
        "raw": rows[:20],
    }


def _final_rating(signals: List[str]) -> str:
    red = sum(1 for s in signals if s == "RED")
    yellow = sum(1 for s in signals if s == "YELLOW")
    if red >= 3:
        return "HIGH"
    if red >= 1 or yellow >= 2:
        return "MEDIUM-HIGH"
    return "LOW"


def scan_dump_risk(contract_address: str, chain: str = "bsc", creator_address: Optional[str] = None) -> Dict:
    """Run integrated dump-detective style risk scan."""
    if not contract_address or not contract_address.startswith("0x"):
        raise ValueError("contract_address 必须是 0x 开头地址")

    chain_key = (chain or "bsc").lower()
    chain_id = CHAIN_MAP.get(chain_key, CHAIN_MAP["bsc"])

    audit = _step_audit(chain_id, contract_address)
    dynamic = _step_market_dynamic(chain_id, contract_address)
    smart = _step_smart_money(chain_id, contract_address)
    hype = _step_hype_proxy(dynamic)
    creator = _step_creator_wallet(chain_id, creator_address)

    signals = []
    details = []

    # 1) Contract safety
    if int(audit.get("risk_level", 0)) >= 2 or audit.get("high_risk_count", 0) > 0:
        signals.append("RED")
        details.append("合约安全存在高风险项")
    elif audit.get("buy_tax", 0) > 10 or audit.get("sell_tax", 0) > 10:
        signals.append("YELLOW")
        details.append("买卖税较高")
    else:
        signals.append("GREEN")

    # 2) Buy/Sell pressure + holders
    if dynamic.get("sell_ratio", 0) >= 0.60:
        signals.append("RED")
        details.append("24h卖压超过60%")
    elif dynamic.get("sell_ratio", 0) >= 0.52:
        signals.append("YELLOW")
        details.append("24h卖压偏高")
    else:
        signals.append("GREEN")

    # 3) Smart money
    if not smart.get("in_smart_money_board") and dynamic.get("smart_money_holders", 0) == 0:
        signals.append("RED")
        details.append("Smart Money 持仓和信号都偏弱")
    elif dynamic.get("smart_money_holders", 0) <= 3:
        signals.append("YELLOW")
        details.append("Smart Money 持仓较低")
    else:
        signals.append("GREEN")

    # 4) Hype proxy
    if hype.get("state") == "FADING":
        signals.append("YELLOW")
        details.append("交易热度衰减")
    elif hype.get("state") == "HOT":
        signals.append("GREEN")
    else:
        signals.append("GREEN")

    # 5) Creator wallet if available
    if creator.get("checked") and creator.get("available"):
        if creator.get("has_active_positions") is False:
            signals.append("RED")
            details.append("Creator 钱包无活跃仓位")
        else:
            signals.append("GREEN")
    elif creator.get("checked") and not creator.get("available"):
        signals.append("YELLOW")
        details.append("Creator 钱包接口暂不可用")

    rating = _final_rating(signals)

    return {
        "contract_address": contract_address,
        "chain": chain_key,
        "rating": rating,
        "summary": details,
        "steps": {
            "token_audit": audit,
            "token_dynamic": dynamic,
            "smart_money": smart,
            "hype_proxy": hype,
            "creator_wallet": creator,
        },
        "risk_signals": signals,
        "note": "结果用于风险提示，不构成投资建议",
    }
