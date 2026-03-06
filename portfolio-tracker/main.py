# Portfolio Tracker
import os
import requests
import time
from datetime import datetime

API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")
BASE_URL = "https://api.binance.com"

def get_account():
    """Get account balances"""
    if not API_KEY:
        print("⚠️ API key not configured")
        return None
    
    url = f"{BASE_URL}/api/v3/account"
    import hmac, hashlib
    params = {"timestamp": int(time.time() * 1000)}
    query_string = "&".join([f"{k}={v}" for k,v in sorted(params.items())])
    params["signature"] = hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    headers = {"X-MBX-APIKEY": API_KEY}
    
    resp = requests.get(url, params=params, headers=headers)
    return resp.json()

def get_prices():
    """Get all USDT prices"""
    url = f"{BASE_URL}/api/v3/ticker/price"
    resp = requests.get(url)
    return {p["symbol"]: float(p["price"]) for p in resp.json() if p["symbol"].endswith("USDT")}

def get_price(symbol):
    """Get price for a symbol"""
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params)
    return float(resp.json()["price"])

def main():
    print("💰 Portfolio Tracker")
    print("=" * 50)
    
    prices = get_prices()
    account = get_account()
    
    if not account:
        print("Configure BINANCE_API_KEY and BINANCE_SECRET_KEY")
        return
    
    total_usdt = 0
    print(f"\n{'Asset':<10} {'Balance':<15} {'Price':<15} {'Value (USDT)':<15}")
    print("-" * 55)
    
    for balance in account["balances"]:
        asset = balance["asset"]
        free = float(balance["free"])
        locked = float(balance["locked"])
        total = free + locked
        
        if total > 0:
            if asset == "USDT":
                value = total
                print(f"{asset:<10} {total:<15.4f} {'1.0000':<15} {value:<15.2f}")
            else:
                symbol = f"{asset}USDT"
                if symbol in prices:
                    value = total * prices[symbol]
                    print(f"{asset:<10} {total:<15.4f} {prices[symbol]:<15.2f} {value:<15.2f}")
                elif asset in prices:
                    value = total * prices[asset]
                    print(f"{asset:<10} {total:<15.4f} {prices[asset]:<15.2f} {value:<15.2f}")
            
            if asset in ["USDT", "BTC", "ETH", "BNB"]:
                total_usdt += value
    
    print("-" * 55)
    print(f"Total: ${total_usdt:,.2f}")

if __name__ == "__main__":
    main()
