"""
AI Post Generator for Binance
Generate ready-to-post market insights with one command
"""
import os
from indicators.indicators import analyze_market
from utils.binance_api import get_price, get_24h_ticker, get_klines
from utils.whale_tracker import get_open_interest, get_market_sentiment

# OpenAI for generating insights
try:
    # from openai import OpenAI  # Using OpenClaw AI instead
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except:
    client = None

def get_market_data(symbol: str) -> dict:
    """Get comprehensive market data"""
    symbol = symbol.upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    try:
        price = get_price(symbol)
        ticker = get_24h_ticker(symbol)
        klines = get_klines(symbol, "1h", 50)
        prices = [k["close"] for k in klines]
        analysis = analyze_market(prices)
        
        # Get OI data
        try:
            oi = get_open_interest(symbol.replace("USDT", ""))
        except:
            oi = {}
        
        sentiment = get_market_sentiment(symbol.replace("USDT", ""))
        
        return {
            "symbol": symbol,
            "price": price,
            "change_24h": ticker["change_24h"],
            "rsi": analysis.get("rsi", 50),
            "trend": analysis.get("trend", "震荡"),
            "signal": analysis.get("signal", "观望"),
            "oi": oi.get("open_interest", 0),
            "oi_change": oi.get("change_24h", 0),
            "sentiment": sentiment
        }
    except Exception as e:
        return {"error": str(e)}

def generate_post_basic(symbol: str) -> str:
    """Generate basic post without AI"""
    data = get_market_data(symbol)
    
    if "error" in data:
        return f"❌ 获取数据失败: {data['error']}"
    
    symbol_clean = data["symbol"].replace("USDT", "")
    
    # Format price
    if data["price"] > 1000:
        price_str = f"${data['price']:,.0f}"
    else:
        price_str = f"${data['price']:,.2f}"
    
    # Format OI
    oi_str = f"${data['oi']/1e9:.1f}B" if data["oi"] > 0 else "N/A"
    
    # Emoji based on change
    if data["change_24h"] > 3:
        emoji = "🚀"
    elif data["change_24h"] > 0:
        emoji = "📈"
    elif data["change_24h"] > -3:
        emoji = "📉"
    else:
        emoji = "💥"
    
    # Generate opinion
    opinion = ""
    if data["signal"] == "买入":
        opinion = "短期有望继续上涨，但需关注关键阻力位"
    elif data["signal"] == "卖出":
        opinion = "注意风险，建议观望或减仓"
    else:
        opinion = "建议保持中性，等待更多信号"
    
    post = f"""
{emoji} {symbol_clean} 实时分析

💰 当前: {price_str} ({data['change_24h']:+.2f}%)
📈 RSI: {data['rsi']} ({data['trend']})
🐋 OI: {oi_str} ({data['oi_change']:+.1f}%)
🎭 情绪: {data['sentiment']}

观点: {opinion}
#{symbol_clean} #加密货币 #交易
"""
    
    return post.strip()

def generate_post_ai(symbol: str) -> str:
    """Generate post with AI enhancement"""
    data = get_market_data(symbol)
    
    if "error" in data:
        return f"❌ 获取数据失败: {data['error']}"
    
    if not client:
        return generate_post_basic(symbol) + "\n\n⚠️ 添加 OPENAI_API_KEY 获取AI增强版本"
    
    symbol_clean = data["symbol"].replace("USDT", "")
    
    # Build context
    context = f"""
Symbol: {symbol_clean}
Price: ${data['price']:.2f}
24h Change: {data['change_24h']:+.2f}%
RSI: {data['rsi']}
Trend: {data['trend']}
Signal: {data['signal']}
OI Change: {data['oi_change']:+.1f}%
Sentiment: {data['sentiment']}
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a crypto analyst generating viral social media posts.
Create exciting, concise market insights (within 280 chars for Twitter).
Use emojis appropriately.
Include 2-3 relevant hashtags.
End with a brief market opinion."""},
                {"role": "user", "content": f"Generate a viral crypto post for {symbol_clean} with this data:\n{context}"}
            ],
            max_tokens=200
        )
        
        ai_post = response.choices[0].message.content
        
        # Add data footer
        footer = f"\n\n💰 ${data['price']:,.0f} ({data['change_24h']:+.1f}%) | RSI:{data['rsi']}"
        
        return (ai_post + footer).strip()
        
    except Exception as e:
        return generate_post_basic(symbol)

def generate_thread(symbol: str) -> str:
    """Generate a Twitter thread"""
    data = get_market_data(symbol)
    
    if "error" in data:
        return f"❌ 获取数据失败: {data['error']}"
    
    symbol_clean = data["symbol"].replace("USDT", "")
    
    thread = []
    
    # Tweet 1: Hook
    thread.append(f"🧵 {symbol_clean} 深度分析\n\n可能改变你接下来的交易决策 👇")
    
    # Tweet 2: Price action
    change_emoji = "🟢" if data["change_24h"] > 0 else "🔴"
    thread.append(f"📊 价格走势\n\n{change_emoji} 当前: ${data['price']:,.2f}\n24h: {data['change_24h']:+.2f}%\n\n趋势: {data['trend']}")
    
    # Tweet 3: Technicals
    rsi_emoji = "🔥" if data["rsi"] > 70 else "❄️" if data["rsi"] < 30 else "⚖️"
    thread.append(f"📈 技术指标\n\nRSI: {data['rsi']} {rsi_emoji}\n信号: {data['signal']}\n\n{data.get('reasons', '无明显信号')}")
    
    # Tweet 4: Whale activity
    oi_str = f"${data['oi']/1e9:.1f}B" if data["oi"] > 0 else "N/A"
    thread.append(f"🐋 巨鲸动向\n\n持仓: {oi_str}\n变化: {data['oi_change']:+.1f}%\n情绪: {data['sentiment']}")
    
    # Tweet 5: Opinion
    thread.append(f"🎯 我的观点\n\n{data['signal']}\n\n⚠️ 仅供参考，不构成投资建议\n\n#crypto #{symbol_clean}USDT")
    
    return "\n\n---\n\n".join(thread)

def main():
    """Interactive post generator"""
    print("=" * 50)
    print("📝 AI Post Generator")
    print("=" * 50)
    print("\n用法:")
    print("  python post_generator.py BTC       - 基础版")
    print("  python post_generator.py BTC ai    - AI增强版")
    print("  python post_generator.py BTC thread - 推文串")
    print()
    
    import sys
    if len(sys.argv) < 2:
        symbol = input("输入币种 (BTC/ETH/SOL): ").strip()
    else:
        symbol = sys.argv[1]
    
    mode = sys.argv[2] if len(sys.argv) > 2 else "basic"
    
    print(f"\n🔄 生成 {symbol} 分析中...\n")
    
    if mode == "thread":
        print(generate_thread(symbol))
    elif mode == "ai":
        print(generate_post_ai(symbol))
    else:
        print(generate_post_basic(symbol))

if __name__ == "__main__":
    main()
