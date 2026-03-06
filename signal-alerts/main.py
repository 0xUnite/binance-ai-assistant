# Signal Alerts
import os
import time
import requests
from datetime import datetime

SYMBOL = os.getenv("ALERT_SYMBOL", "BTCUSDT")
PRICE_ABOVE = float(os.getenv("PRICE_ABOVE", "0"))
PRICE_BELOW = float(os.getenv("PRICE_BELOW", "0"))
CHECK_INTERVAL = 30  # seconds
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

BASE_URL = "https://api.binance.com"

def get_price(symbol):
    url = f"{BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    resp = requests.get(url, params=params)
    return float(resp.json()["price"])

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"📱 Telegram not configured, skipping notification")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Telegram error: {e}")

def main():
    print(f"🔔 Price Alert Bot for {SYMBOL}")
    print(f"Above: ${PRICE_ABOVE:,.2f} | Below: ${PRICE_BELOW:,.2f}")
    print("-" * 40)
    
    notified_above = False
    notified_below = False
    
    while True:
        try:
            price = get_price(SYMBOL)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {SYMBOL}: ${price:,.2f}")
            
            if PRICE_ABOVE > 0 and price >= PRICE_ABOVE and not notified_above:
                msg = f"🚀 {SYMBOL} reached ${price:,.2f} (above ${PRICE_ABOVE:,.2f})"
                print(f"✅ {msg}")
                send_telegram(msg)
                notified_above = True
            
            if PRICE_BELOW > 0 and price <= PRICE_BELOW and not notified_below:
                msg = f"🔻 {SYMBOL} dropped to ${price:,.2f} (below ${PRICE_BELOW:,.2f})"
                print(f"✅ {msg}")
                send_telegram(msg)
                notified_below = True
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
