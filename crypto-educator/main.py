# Crypto Educator
import os
import requests
# from openai import OpenAI  # Using OpenClaw AI instead

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BASE_URL = "https://api.binance.com"

# System prompt for crypto education
SYSTEM_PROMPT = """You are a knowledgeable crypto educator specializing in Binance products and trading.
You help users understand:
- Binance products (Spot, Futures, Margin, etc.)
- Trading concepts (RSI, MACD, MA, Bollinger Bands)
- Risk management
- Market analysis

Provide clear, accurate explanations. If unsure, say so."""

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def get_market_data(symbol="BTCUSDT"):
    """Get current market data from Binance"""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        return {
            "price": float(data["lastPrice"]),
            "change_24h": float(data["priceChangePercent"]),
            "high_24h": float(data["highPrice"]),
            "low_24h": float(data["lowPrice"]),
            "volume": float(data["volume"])
        }
    except:
        return None

def get_top_coins(limit=10):
    """Get top coins by volume"""
    url = f"{BASE_URL}/api/v3/ticker/24hr"
    try:
        resp = requests.get(url)
        data = resp.json()
        # Filter USDT pairs and sort by volume
        usdt_pairs = [d for d in data if d["symbol"].endswith("USDT")]
        sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x["quoteVolume"]), reverse=True)
        return sorted_pairs[:limit]
    except:
        return []

def chat_with_ai(question):
    """Chat with AI about crypto"""
    if not client:
        return "OpenAI API key not configured. Set OPENAI_API_KEY environment variable."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    print("📚 Crypto Educator")
    print("=" * 50)
    print("Ask me anything about crypto trading!")
    print("Commands:")
    print("  /price <symbol> - Get price info")
    print("  /top - Top coins by volume")
    print("  /help - Show this help")
    print("  /quit - Exit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n❓ You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.startswith("/price "):
                symbol = user_input.split("/price ")[1].upper()
                data = get_market_data(symbol)
                if data:
                    print(f"\n📊 {symbol}")
                    print(f"   Price: ${data['price']:,.2f}")
                    print(f"   24h Change: {data['change_24h']:+.2f}%")
                    print(f"   High: ${data['high_24h']:,.2f}")
                    print(f"   Low: ${data['low_24h']:,.2f}")
                else:
                    print(f"❌ Could not find {symbol}")
            
            elif user_input == "/top":
                print("\n🔥 Top Coins by Volume:")
                coins = get_top_coins()
                for i, coin in enumerate(coins, 1):
                    print(f"   {i}. {coin['symbol']} - ${float(coin['quoteVolume']):,.0f}")
            
            elif user_input == "/help":
                print("\nCommands:")
                print("  /price <symbol> - Get price info")
                print("  /top - Top coins by volume")
                print("  /help - Show this help")
            
            elif user_input == "/quit":
                print("👋 Goodbye!")
                break
            
            else:
                print("\n🤖 ", end="")
                print(chat_with_ai(user_input))
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

if __name__ == "__main__":
    main()
