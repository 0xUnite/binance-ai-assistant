"""
Binance API Utility
Unified API calls for all Binance endpoints
"""
import os
import time
import hmac
import hashlib
import requests
from typing import Dict, List, Optional

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")
BASE_URL = "https://api.binance.com"

def get_signature(secret: str, params: dict) -> str:
    """Generate HMAC SHA256 signature"""
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_price(symbol: str) -> float:
    """Get current price"""
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol.upper()}
    resp = requests.get(url, params=params)
    return float(resp.json()["price"])

def get_24h_ticker(symbol: str) -> Dict:
    """Get 24h ticker data"""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol.upper()}
    resp = requests.get(url, params=params)
    data = resp.json()
    return {
        "symbol": data["symbol"],
        "price": float(data["lastPrice"]),
        "change_24h": float(data["priceChangePercent"]),
        "high_24h": float(data["highPrice"]),
        "low_24h": float(data["lowPrice"]),
        "volume_24h": float(data["volume"]),
        "quote_volume_24h": float(data["quoteVolume"]),
        "trades_24h": int(data["count"])
    }

def get_klines(symbol: str, interval: str = "1h", limit: int = 100) -> List:
    """Get candlestick/kline data"""
    url = f"{BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }
    resp = requests.get(url, params=params)
    klines = resp.json()
    
    result = []
    for k in klines:
        result.append({
            "open_time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5]),
            "close_time": k[6]
        })
    return result

def get_depth(symbol: str, limit: int = 20) -> Dict:
    """Get order book depth"""
    url = f"{BASE_URL}/api/v3/depth"
    params = {"symbol": symbol.upper(), "limit": limit}
    resp = requests.get(url, params=params)
    data = resp.json()
    
    return {
        "bids": [[float(p), float(q)] for p, q in data["bids"]],
        "asks": [[float(p), float(q)] for p, q in data["asks"]]
    }

def get_recent_trades(symbol: str, limit: int = 20) -> List:
    """Get recent trades"""
    url = f"{BASE_URL}/api/v3/trades"
    params = {"symbol": symbol.upper(), "limit": limit}
    resp = requests.get(url, params=params)
    return resp.json()

def get_funding_rate(symbol: str) -> Dict:
    """Get funding rate (for futures)"""
    url = f"{BASE_URL}/api/v3/premiumIndex"
    params = {"symbol": symbol.upper()}
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        return {
            "symbol": data["symbol"],
            "mark_price": float(data["markPrice"]),
            "index_price": float(data["indexPrice"]),
            "funding_rate": float(data["lastFundingRate"]) * 100,
            "next_funding_time": data["nextFundingTime"]
        }
    except:
        return {"error": "Not a futures symbol"}

def get_exchange_info() -> Dict:
    """Get exchange trading rules"""
    url = f"{BASE_URL}/api/v3/exchangeInfo"
    resp = requests.get(url)
    return resp.json()

def get_trading_fee(symbol: str) -> Dict:
    """Get trading fee rate"""
    if not API_KEY or not API_SECRET:
        return {"maker_fee": 0.02, "taker_fee": 0.04}  # Default
    
    url = f"{BASE_URL}/api/v3/account"
    params = {"timestamp": int(time.time() * 1000)}
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    
    # Find symbol fee
    for s in data.get("balances", []):
        if s["asset"] == symbol.replace("USDT", ""):
            return {"message": "Use /api/v3/ticker/24hr for actual fees"}
    
    return {"maker_fee": 0.02, "taker_fee": 0.04}

def get_all_prices() -> Dict:
    """Get all USDT pair prices"""
    url = f"{BASE_URL}/api/v3/ticker/price"
    resp = requests.get(url)
    prices = {}
    for item in resp.json():
        if item["symbol"].endswith("USDT"):
            prices[item["symbol"]] = float(item["price"])
    return prices

def get_top_coins(limit: int = 10) -> List:
    """Get top coins by volume"""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    resp = requests.get(url)
    data = resp.json()
    
    usdt_pairs = [d for d in data if d["symbol"].endswith("USDT")]
    sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x["quoteVolume"]), reverse=True)
    
    result = []
    for p in sorted_pairs[:limit]:
        result.append({
            "symbol": p["symbol"],
            "price": float(p["lastPrice"]),
            "change_24h": float(p["priceChangePercent"]),
            "volume_24h": float(p["quoteVolume"])
        })
    return result

def get_account_balance() -> List:
    """Get account balances (requires API key)"""
    if not API_KEY or not API_SECRET:
        return []
    
    url = f"{BASE_URL}/api/v3/account"
    params = {"timestamp": int(time.time() * 1000)}
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    
    balances = []
    for b in data.get("balances", []):
        free = float(b.get("free", 0))
        locked = float(b.get("locked", 0))
        if free + locked > 0:
            balances.append({
                "asset": b["asset"],
                "free": free,
                "locked": locked,
                "total": free + locked
            })
    return balances

def place_order(symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> Dict:
    """Place an order (requires API key)"""
    if not API_KEY or not API_SECRET:
        return {"error": "API keys required"}
    
    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "type": order_type,
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }
    params["signature"] = get_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        resp = requests.post(url, params=params, headers=headers)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# Alpha/Binance specific endpoints
def get_binance_alpha_tokens() -> List:
    """Get trending Alpha tokens on Binance"""
    # This is a simplified version - in production would use Binance API
    # For now return commonly known Alpha tokens
    return [
        {"symbol": "DEEPUS": "DeepBook"},
        {"symbolDT", "name": "VELAUSDT", "name": "Vela"},
        {"symbol": "RIXUSDT", "name": "Rix"}
    ]

def get_announcements() -> List:
    """Get latest Binance announcements"""
    url = "https://www.binance.com/bapi/cms/v1/article/list"
    params = {
        "catalogId": 48,  # News catalog
        "pageNo": 1,
        "pageSize": 5
    }
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        articles = []
        for item in data.get("data", {}).get("articles", [])[:5]:
            articles.append({
                "title": item.get("title", ""),
                "date": item.get("publishDate", ""),
                "url": f"https://www.binance.com/en/support/articles/{item.get('articleId', '')}"
            })
        return articles
    except:
        return []
