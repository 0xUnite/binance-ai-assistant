# Binance Trading Bot
import os
import time
import hmac
import hashlib
import requests
from datetime import datetime

# Configuration
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")
SYMBOL = "BTCUSDT"
RSI_PERIOD = 14
TRADE_QUANTITY = 0.001

BASE_URL = "https://api.binance.com"

def get_binance_signature(secret, params):
    """Generate HMAC SHA256 signature"""
    query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    signature = hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    return signature

def get_klines(symbol, interval="1h", limit=100):
    """Get candlestick data"""
    url = f"{BASE_URL}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params)
    return resp.json()

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def place_order(symbol, side, quantity):
    """Place market order"""
    if not API_KEY or not API_SECRET:
        print("⚠️ API keys not configured. Set BINANCE_API_KEY and BINANCE_SECRET_KEY")
        return None
    
    url = f"{BASE_URL}/api/v3/order"
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": int(time.time() * 1000)
    }
    params["signature"] = get_binance_signature(API_SECRET, params)
    headers = {"X-MBX-APIKEY": API_KEY}
    
    try:
        resp = requests.post(url, params=params, headers=headers)
        return resp.json()
    except Exception as e:
        print(f"Order error: {e}")
        return None

def run_strategy():
    """Main trading strategy loop"""
    print("🤖 Binance Trading Bot Started")
    print(f"Symbol: {SYMBOL}, RSI Period: {RSI_PERIOD}")
    print("-" * 40)
    
    while True:
        try:
            klines = get_klines(SYMBOL)
            closes = [float(k[4]) for k in klines]
            
            rsi = calculate_rsi(closes, RSI_PERIOD)
            current_price = closes[-1]
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Price: ${current_price:,.2f} | RSI: {rsi:.2f}")
            
            # Simple strategy: Buy when RSI < 30, Sell when RSI > 70
            if rsi < 30:
                print("📈 RSI < 30 - BUY SIGNAL!")
                result = place_order(SYMBOL, "BUY", TRADE_QUANTITY)
                if result and "orderId" in result:
                    print(f"✅ Buy order placed: {result.get('orderId')}")
            elif rsi > 70:
                print("📉 RSI > 70 - SELL SIGNAL!")
                result = place_order(SYMBOL, "SELL", TRADE_QUANTITY)
                if result and "orderId" in result:
                    print(f"✅ Sell order placed: {result.get('orderId')}")
            
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run_strategy()
