"""
Binance API Utility
Unified API calls for Binance Spot/Futures endpoints.
"""
import os
import time
import hmac
import hashlib
from typing import Dict, List, Any

import requests

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")
BASE_URL = "https://api.binance.com"
FUTURES_BASE_URL = "https://fapi.binance.com"
DEFAULT_TIMEOUT = 12


def get_signature(secret: str, params: dict) -> str:
    """Generate HMAC SHA256 signature."""
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()


def _request_json(method: str, url: str, **kwargs) -> Any:
    """Execute HTTP request and normalize Binance API errors."""
    kwargs.setdefault("timeout", DEFAULT_TIMEOUT)
    resp = requests.request(method, url, **kwargs)

    content_type = resp.headers.get("Content-Type", "")
    if "application/json" not in content_type:
        resp.raise_for_status()
        raise RuntimeError(f"Unexpected response format: {content_type}")

    data = resp.json()

    if resp.status_code >= 400:
        if isinstance(data, dict) and "msg" in data:
            raise RuntimeError(data["msg"])
        raise RuntimeError(f"HTTP {resp.status_code}")

    if isinstance(data, dict) and "code" in data and data.get("code", 0) < 0:
        raise RuntimeError(data.get("msg", "Binance API error"))

    return data


def get_price(symbol: str) -> float:
    """Get current price."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    data = _request_json("GET", url, params={"symbol": symbol.upper()})
    return float(data["price"])


def get_24h_ticker(symbol: str) -> Dict:
    """Get 24h ticker data."""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    data = _request_json("GET", url, params={"symbol": symbol.upper()})
    return {
        "symbol": data["symbol"],
        "price": float(data["lastPrice"]),
        "change_24h": float(data["priceChangePercent"]),
        "high_24h": float(data["highPrice"]),
        "low_24h": float(data["lowPrice"]),
        "volume_24h": float(data["volume"]),
        "quote_volume_24h": float(data["quoteVolume"]),
        "trades_24h": int(data["count"]),
    }


def get_klines(symbol: str, interval: str = "1h", limit: int = 100) -> List:
    """Get candlestick/kline data."""
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": max(1, min(limit, 1000)),
    }
    klines = _request_json("GET", url, params=params)

    result = []
    for k in klines:
        result.append(
            {
                "open_time": k[0],
                "open": float(k[1]),
                "high": float(k[2]),
                "low": float(k[3]),
                "close": float(k[4]),
                "volume": float(k[5]),
                "close_time": k[6],
            }
        )
    return result


def get_depth(symbol: str, limit: int = 20) -> Dict:
    """Get order book depth."""
    url = f"{BASE_URL}/api/v3/depth"
    safe_limit = max(5, min(limit, 5000))
    data = _request_json("GET", url, params={"symbol": symbol.upper(), "limit": safe_limit})

    return {
        "bids": [[float(p), float(q)] for p, q in data["bids"]],
        "asks": [[float(p), float(q)] for p, q in data["asks"]],
    }


def get_recent_trades(symbol: str, limit: int = 20) -> List:
    """Get recent trades."""
    url = f"{BASE_URL}/api/v3/trades"
    safe_limit = max(1, min(limit, 1000))
    return _request_json("GET", url, params={"symbol": symbol.upper(), "limit": safe_limit})


def get_funding_rate(symbol: str) -> Dict:
    """Get funding rate for perpetual futures symbols."""
    url = f"{FUTURES_BASE_URL}/fapi/v1/premiumIndex"
    try:
        data = _request_json("GET", url, params={"symbol": symbol.upper()})
        return {
            "symbol": data["symbol"],
            "mark_price": float(data["markPrice"]),
            "index_price": float(data["indexPrice"]),
            "funding_rate": float(data["lastFundingRate"]) * 100,
            "next_funding_time": int(data["nextFundingTime"]),
        }
    except Exception:
        return {"error": "Not a futures symbol"}


def get_exchange_info() -> Dict:
    """Get exchange trading rules."""
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    return _request_json("GET", url)


def get_trading_fee(symbol: str = "BTCUSDT") -> Dict:
    """Get account-level trading fee (placeholder if API key not configured)."""
    if not API_KEY or not API_SECRET:
        return {"maker_fee": 0.02, "taker_fee": 0.04}

    url = f"{BASE_URL}/api/v3/account"
    params = {"timestamp": int(time.time() * 1000)}
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}

    data = _request_json("GET", url, params=params, headers=headers)

    for balance in data.get("balances", []):
        if balance.get("asset") == symbol.replace("USDT", ""):
            return {"message": "Use exchange VIP fee schedule / commission endpoints for exact fee."}

    return {"maker_fee": 0.02, "taker_fee": 0.04}


def get_all_prices() -> Dict:
    """Get all USDT pair prices."""
    url = f"{BASE_URL}/api/v3/ticker/price"
    data = _request_json("GET", url)
    prices = {}
    for item in data:
        if item["symbol"].endswith("USDT"):
            prices[item["symbol"]] = float(item["price"])
    return prices


def get_top_coins(limit: int = 10) -> List:
    """Get top coins by quote volume."""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    data = _request_json("GET", url)

    usdt_pairs = [d for d in data if d["symbol"].endswith("USDT")]
    sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x["quoteVolume"]), reverse=True)

    result = []
    for pair in sorted_pairs[: max(1, limit)]:
        result.append(
            {
                "symbol": pair["symbol"],
                "price": float(pair["lastPrice"]),
                "change_24h": float(pair["priceChangePercent"]),
                "volume_24h": float(pair["quoteVolume"]),
            }
        )
    return result


def get_account_balance() -> List:
    """Get account balances (requires API key)."""
    if not API_KEY or not API_SECRET:
        return []

    url = f"{BASE_URL}/api/v3/account"
    params = {"timestamp": int(time.time() * 1000)}
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}

    data = _request_json("GET", url, params=params, headers=headers)

    balances = []
    for item in data.get("balances", []):
        free = float(item.get("free", 0))
        locked = float(item.get("locked", 0))
        if free + locked > 0:
            balances.append(
                {
                    "asset": item["asset"],
                    "free": free,
                    "locked": locked,
                    "total": free + locked,
                }
            )
    return balances


def place_order(symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> Dict:
    """Place an order (requires API key)."""
    if not API_KEY or not API_SECRET:
        return {"error": "API keys required"}

    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type,
        "quantity": quantity,
        "timestamp": int(time.time() * 1000),
    }
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}

    try:
        return _request_json("POST", url, params=params, headers=headers)
    except Exception as e:
        return {"error": str(e)}


def get_binance_alpha_tokens() -> List:
    """Get sample trending Alpha tokens."""
    return [
        {"symbol": "DEEPUSDT", "name": "DeepBook"},
        {"symbol": "VELAUSDT", "name": "Vela"},
        {"symbol": "RIXUSDT", "name": "Rix"},
    ]


def get_announcements() -> List:
    """Get latest Binance announcements."""
    url = "https://www.binance.com/bapi/cms/v1/article/list"
    params = {
        "catalogId": 48,
        "pageNo": 1,
        "pageSize": 5,
    }
    try:
        data = _request_json("GET", url, params=params)
        articles = []
        for item in data.get("data", {}).get("articles", [])[:5]:
            articles.append(
                {
                    "title": item.get("title", ""),
                    "date": item.get("publishDate", ""),
                    "url": f"https://www.binance.com/en/support/articles/{item.get('articleId', '')}",
                }
            )
        return articles
    except Exception:
        return []
