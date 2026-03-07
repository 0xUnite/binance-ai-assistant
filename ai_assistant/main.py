"""
Binance AI Assistant
Powered by OpenClaw + Claude
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from indicators.indicators import analyze_market, calculate_rsi, calculate_ma
from utils.binance_api import (
    get_price, get_24h_ticker, get_klines, get_depth,
    get_funding_rate, get_top_coins, get_account_balance,
    get_announcements, get_all_prices
)

# OpenClaw AI (built-in)
from utils.ai_helper import ask_ai, generate_trading_idea

class BinanceAI:
    """Binance AI Assistant"""
    
    def __init__(self):
        self.name = "Binance AI Assistant"
        self.version = "3.0.0"
    
    def get_market_summary(self, symbol: str = "BTCUSDT") -> str:
        """Get comprehensive market summary"""
        try:
            ticker = get_24h_ticker(symbol)
            klines = get_klines(symbol, "1h", 50)
            
            if not klines:
                return f"无法获取 {symbol} 数据"
            
            prices = [k["close"] for k in klines]
            analysis = analyze_market(prices)
            
            return f"""
📊 {symbol} 市场分析

💰 当前价格: ${ticker['price']:,.2f}
📈 24h涨跌: {ticker['change_24h']:+.2f}%
📊 24h高: ${ticker['high_24h']:,.2f}
📉 24h低: ${ticker['low_24h']:,.2f}

📈 技术指标:
• RSI(14): {analysis['rsi']}
• MACD: {analysis['macd']['histogram']:+.2f}
• MA20: ${analysis['ma20']:,.2f}
• 趋势: {analysis['trend']}
• 信号: {analysis['signal']}

💡 {analysis['reasons']}
"""
        except Exception as e:
            return f"获取数据失败: {str(e)}"
    
    def get_price_info(self, symbol: str) -> str:
        """Get price info for a symbol"""
        try:
            price = get_price(symbol)
            ticker = get_24h_ticker(symbol)
            return f"""
{symbol} 价格信息

💰 当前: ${price:,.2f}
📈 24h: {ticker['change_24h']:+.2f}%
📊 最高: ${ticker['high_24h']:,.2f}
📉 最低: ${ticker['low_24h']:,.2f}
📦 24h成交量: ${ticker['quote_volume_24h']:,.0f}
"""
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def get_orderbook(self, symbol: str) -> str:
        """Get order book depth"""
        try:
            depth = get_depth(symbol, 10)
            bids = depth["bids"][:5]
            asks = depth["asks"][:5]
            
            msg = f"📊 {symbol} 订单簿\n\n"
            msg += "买单 (Bids)          卖单 (Asks)\n"
            msg += "-" * 35 + "\n"
            
            for i in range(5):
                bid_p, bid_q = bids[i]
                ask_p, ask_q = asks[i]
                msg += f"${bid_p:,.2f}  {bid_q:.4f}    ${ask_p:,.2f}  {ask_q:.4f}\n"
            
            spread = asks[0][0] - bids[0][0]
            msg += f"\n价差: ${spread:,.2f} ({spread/bids[0][0]*100:.3f}%)"
            
            return msg
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def get_top_coins_report(self) -> str:
        """Get top coins by volume"""
        try:
            coins = get_top_coins(10)
            msg = "🔥 热门代币 (24h成交量)\n\n"
            
            for i, coin in enumerate(coins, 1):
                msg += f"{i}. {coin['symbol']}\n"
                msg += f"   ${coin['price']:,.4f}  {coin['change_24h']:+.2f}%\n"
                msg += f"   成交量: ${coin['volume_24h']:,.0f}\n\n"
            
            return msg
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def get_portfolio(self) -> str:
        """Get portfolio/balance"""
        try:
            balances = get_account_balance()
            if not balances:
                return "请配置 BINANCE_API_KEY 和 BINANCE_SECRET_KEY"
            
            prices = get_all_prices()
            
            msg = "💼 钱包余额\n\n"
            total_usdt = 0
            
            for b in balances[:10]:  # Top 10
                asset = b["asset"]
                total = b["total"]
                
                if asset == "USDT":
                    value = total
                    total_usdt += value
                    msg += f"🟡 USDT: {total:.4f} (${value:,.2f})\n"
                elif f"{asset}USDT" in prices:
                    value = total * prices[f"{asset}USDT"]
                    total_usdt += value
                    msg += f"🔵 {asset}: {total:.4f} (${value:,.2f})\n"
            
            msg += f"\n💰 总计: ${total_usdt:,.2f}"
            return msg
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def get_funding_info(self, symbol: str) -> str:
        """Get funding rate info"""
        try:
            funding = get_funding_rate(symbol)
            if "error" in funding:
                return f"{symbol} 不是合约交易对"
            
            return f"""
{symbol} 资金费率

📊 标记价格: ${funding['mark_price']:,.2f}
📊 指数价格: ${funding['index_price']:,.2f}
💰 资金费率: {funding['funding_rate']:.4f}%
⏰ 下次结算: {funding['next_funding_time']}
"""
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def get_news(self) -> str:
        """Get latest Binance news"""
        try:
            news = get_announcements()
            if not news:
                return "暂无最新公告"
            
            msg = "📰 币安最新公告\n\n"
            for i, item in enumerate(news, 1):
                msg += f"{i}. {item['title']}\n"
                msg += f"   {item['date']}\n\n"
            
            return msg
        except Exception as e:
            return f"获取失败: {str(e)}"
    
    def chat(self, message: str) -> str:
        """Chat with AI about crypto"""
        try:
            prompt = (
                "你是 Binance AI 助手。请给出简洁、可执行的建议，"
                "并附带风险提示。\n\n用户问题："
                f"{message}"
            )
            return ask_ai(prompt)
        except Exception as e:
            return f"AI 响应失败: {str(e)}"
    
    def process_command(self, user_input: str) -> str:
        """Process user command/input"""
        user_input = user_input.lower().strip()
        
        # Price queries
        if "price" in user_input or "价格" in user_input:
            # Extract symbol
            symbols = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "AVAX", "DOT", "MATIC"]
            for s in symbols:
                if s.lower() in user_input:
                    return self.get_price_info(f"{s}USDT")
            return self.get_price_info("BTCUSDT")
        
        # Market analysis
        if "分析" in user_input or "analysis" in user_input or "技术" in user_input:
            symbols = ["BTC", "ETH", "BNB", "SOL"]
            for s in symbols:
                if s.lower() in user_input:
                    return self.get_market_summary(f"{s}USDT")
            return self.get_market_summary("BTCUSDT")
        
        # Order book
        if "depth" in user_input or "订单" in user_input or "深度" in user_input:
            return self.get_orderbook("BTCUSDT")
        
        # Top coins
        if "top" in user_input or "热门" in user_input or "排行榜" in user_input:
            return self.get_top_coins_report()
        
        # Portfolio
        if "portfolio" in user_input or "余额" in user_input or "钱包" in user_input:
            return self.get_portfolio()
        
        # Funding
        if "funding" in user_input or "资金" in user_input:
            return self.get_funding_info("BTCUSDT")
        
        # News
        if "news" in user_input or "新闻" in user_input or "公告" in user_input:
            return self.get_news()
        
        # Help
        if "help" in user_input or "帮助" in user_input:
            return self.get_help()
        
        # Default: use AI chat
        return self.chat(user_input)
    
    def get_help(self) -> str:
        """Get help message"""
        return """
🤖 Binance AI 助手 v3.0

📋 可用命令:

💰 价格查询
   "BTC价格" / "ETH现在多少钱"
   
📊 市场分析
   "分析BTC" / "ETH技术分析"
   
📈 订单簿
   "查看BTC订单簿"
   
🔥 热门代币
   "热门币有哪些" / "top代币"
   
💼 钱包余额
   "我的余额" / "portfolio"
   
💰 资金费率
   "BTC资金费率"
   
📰 最新公告
   "币安新闻" / "最新公告"
   
💬 AI 对话
   直接输入任何问题！

⚠️ 风险提示: 所有交易建议仅供参考，投资需谨慎
"""

def main():
    """Main interactive loop"""
    ai = BinanceAI()
    
    print("=" * 50)
    print("🤖 Binance AI Assistant v3.0")
    print("=" * 50)
    print(ai.get_help())
    print("\n开始对话...\n")
    
    while True:
        try:
            user_input = input("❓ 你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["quit", "exit", "退出"]:
                print("\n👋 再见!")
                break
            
            print("\n🤖 AI: ", end="")
            response = ai.process_command(user_input)
            print(response)
            print()
            
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}\n")

if __name__ == "__main__":
    main()
