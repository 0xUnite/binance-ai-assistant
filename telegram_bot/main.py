"""
Telegram Bot Interface for Binance AI Assistant
Commands: /start, /portfolio, /analyze, /token, /trade, etc.
"""
import os
import sys
import asyncio

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from indicators.indicators import analyze_market
from utils.binance_api import (
    get_price, get_24h_ticker, get_klines, get_funding_rate,
    get_top_coins, get_account_balance, get_all_prices
)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")

# In-memory user data (in production, use database)
user_positions = {}  # user_id -> positions
user_api_keys = {}  # user_id -> {api_key, api_secret}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show menu"""
    user_id = str(update.effective_user.id)
    
    await update.message.reply_text(
        "🤖 *Binance Market Pulse AI*\n\n"
        "欢迎使用 Binance AI 交易助手！\n\n"
        "📋 *可用命令:*\n"
        "/start - 显示菜单\n"
        "/portfolio - 查看仓位\n"
        "/balance - 查看余额\n"
        "/analyze BTC - 市场分析\n"
        "/token ETH - 代币信息\n"
        "/trade SOL - 交易计划\n"
        "/top - 热门代币\n"
        "/funds - 资金信息\n\n"
        "💬 也可直接输入问题！",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    await update.message.reply_text(
        "📋 *命令列表:*\n\n"
        "🔹 /start - 启动\n"
        "🔹 /portfolio - 仓位\n"
        "🔹 /balance - 余额\n"
        "🔹 /analyze <币种> - 分析\n"
        "🔹 /token <币种> - 代币信息\n"
        "🔹 /trade <币种> - 交易计划\n"
        "🔹 /top - 热门榜\n"
        "🔹 /funds - 资金\n\n"
        "💬 也可直接问我问题！",
        parse_mode="Markdown"
    )

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user portfolio/positions"""
    user_id = str(update.effective_user.id)
    
    if user_id not in user_positions or not user_positions[user_id]:
        await update.message.reply_text(
            "📊 *当前仓位:*\n\n"
            "暂无持仓\n\n"
            "使用 /analyze 或 /trade 发现机会",
            parse_mode="Markdown"
        )
        return
    
    positions = user_positions[user_id]
    msg = "📊 *当前持仓*\n\n"
    
    total_pnl = 0
    for pos in positions:
        pnl = pos.get("pnl", 0)
        total_pnl += pnl
        emoji = "🟢" if pnl >= 0 else "🔴"
        
        msg += f"{emoji} *{pos['symbol']}*\n"
        msg += f"   数量: {pos['quantity']}\n"
        msg += f"   开单价: ${pos['entry']}\n"
        msg += f"   当前: ${pos['current']}\n"
        msg += f"   盈亏: ${pnl:+.2f}\n\n"
    
    msg += f"💰 总盈亏: ${total_pnl:+.2f}"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show account balance"""
    user_id = str(update.effective_user.id)
    
    if user_id in user_api_keys:
        # Use user's API key
        await update.message.reply_text("🔄 查询中...")
        # In production, use user's API key
    else:
        await update.message.reply_text(
            "💰 *账户余额*\n\n"
            "请先连接 Binance API\n"
            "输入: /connect <api_key> <api_secret>",
            parse_mode="Markdown"
        )

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Market analysis command"""
    if not context.args:
        await update.message.reply_text("用法: /analyze BTC")
        return
    
    symbol = context.args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    await update.message.reply_text(f"🔄 分析 {symbol}...")
    
    try:
        ticker = get_24h_ticker(symbol)
        klines = get_klines(symbol, "1h", 50)
        prices = [k["close"] for k in klines]
        
        # Get funding
        funding = get_funding_rate(symbol)
        
        # Analysis
        analysis = analyze_market(prices)
        
        msg = f"📊 *{symbol} 市场分析*\n\n"
        msg += f"💰 价格: ${ticker['price']:,.2f}\n"
        msg += f"📈 24h: {ticker['change_24h']:+.2f}%\n\n"
        
        msg += f"📈 *技术指标*\n"
        msg += f"• RSI: {analysis['rsi']}\n"
        msg += f"• MACD: {analysis['macd']['histogram']:+.2f}\n"
        msg += f"• MA20: ${analysis['ma20']:,.2f}\n"
        msg += f"• 趋势: {analysis['trend']}\n"
        msg += f"• 信号: {analysis['signal']}\n\n"
        
        if "funding_rate" in funding:
            msg += f"💰 资金费率: {funding['funding_rate']:.4f}%\n\n"
        
        msg += f"💡 {analysis['reasons']}"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def token_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Token info command"""
    if not context.args:
        await update.message.reply_text("用法: /token ETH")
        return
    
    symbol = context.args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    await update.message.reply_text(f"🔄 查询 {symbol}...")
    
    try:
        ticker = get_24h_ticker(symbol)
        prices = get_all_prices()
        
        msg = f"🔵 *{symbol} 代币信息*\n\n"
        msg += f"💰 价格: ${ticker['price']:,.4f}\n"
        msg += f"📈 24h涨跌: {ticker['change_24h']:+.2f}%\n"
        msg += f"📊 24h高: ${ticker['high_24h']:,.2f}\n"
        msg += f"📉 24h低: ${ticker['low_24h']:,.2f}\n"
        msg += f"📦 成交量: ${ticker['quote_volume_24h']:,.0f}\n"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def trade_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate trade plan"""
    if not context.args:
        await update.message.reply_text("用法: /trade SOL")
        return
    
    symbol = context.args[0].upper()
    if not symbol.endswith("USDT"):
        symbol += "USDT"
    
    await update.message.reply_text(f"🔄 生成 {symbol} 交易计划...")
    
    try:
        ticker = get_24h_ticker(symbol)
        klines = get_klines(symbol, "4h", 100)
        prices = [k["close"] for k in klines]
        
        current_price = ticker["price"]
        change = ticker["change_24h"]
        
        # Generate trade plan
        entry_low = current_price * 0.95
        entry_high = current_price * 1.02
        
        dca1 = current_price * 0.90
        dca2 = current_price * 0.85
        
        stop_loss = current_price * 0.92
        
        target1 = current_price * 1.10
        target2 = current_price * 1.20
        
        # Determine bias
        bias = "Bullish" if change > 0 else "Bearish"
        
        msg = f"📈 *{symbol} 交易计划*\n\n"
        msg += f"📊 *当前状态*\n"
        msg += f"Bias: {'🟢 看涨' if change > 0 else '🔴 看跌'}\n"
        msg += f"价格: ${current_price:,.2f}\n\n"
        
        msg += f"🎯 *入场区间*\n"
        msg += f"${entry_low:,.2f} - ${entry_high:,.2f}\n\n"
        
        msg += f"📉 *止损*\n"
        msg += f"${stop_loss:,.2f} (-8%)\n\n"
        
        msg += f"💰 *DCA 补仓位*\n"
        msg += f"1. ${dca1:,.2f}\n"
        msg += f"2. ${dca2:,.2f}\n\n"
        
        msg += f"🎯 *目标位*\n"
        msg += f"1. ${target1:,.2f} (+10%)\n"
        msg += f"2. ${target2:,.2f} (+20%)\n\n"
        
        msg += f"⚠️ 建议杠杆: 2-3x\n"
        msg += f"⚠️ 风险提示: 仅供参考"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def top_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show top coins"""
    await update.message.reply_text("🔄 查询热门代币...")
    
    try:
        coins = get_top_coins(10)
        
        msg = "🔥 *热门代币 (24h成交量)*\n\n"
        
        for i, coin in enumerate(coins, 1):
            emoji = "🟢" if coin['change_24h'] > 0 else "🔴"
            msg += f"{i}. {coin['symbol']} {emoji}\n"
            msg += f"   ${coin['price']:,.4f} {coin['change_24h']:+.2f}%\n\n"
        
        await update.message.reply_text(msg, parse_mode="Markdown")
        
    except Exception as e:
        await update.message.reply_text(f"❌ 错误: {str(e)}")

async def funds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show funds info"""
    user_id = str(update.effective_user.id)
    
    await update.message.reply_text(
        "💰 *资金信息*\n\n"
        "🔹 可用余额: 查询中...\n"
        "🔹 总持仓: 查询中...\n"
        "🔹 今日盈亏: 查询中...\n\n"
        "💡 连接 API 获取实时数据\n"
        "输入: /connect <api_key> <api_secret>",
        parse_mode="Markdown"
    )

async def connect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Connect Binance API"""
    user_id = str(update.effective_user.id)
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "用法: /connect <api_key> <api_secret>\n\n"
            "⚠️ 注意: 仅添加交易权限，不要给提现权限",
            parse_mode="Markdown"
        )
        return
    
    api_key = context.args[0]
    api_secret = context.args[1]
    
    user_api_keys[user_id] = {"api_key": api_key, "api_secret": api_secret}
    
    await update.message.reply_text(
        "✅ *API 连接成功！*\n\n"
        "请在 Binance 设置资金和风险限制\n"
        "可用命令: /portfolio /balance /funds",
        parse_mode="Markdown"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages with AI"""
    user_input = update.message.text
    
    # Check if it's a command
    if user_input.startswith("/"):
        await update.message.reply_text("未知命令，输入 /help 查看")
        return
    
    # Simple keyword matching (in production, use AI)
    user_input_lower = user_input.lower()
    
    if "btc" in user_input_lower or "比特币" in user_input_lower:
        context.args = ["BTC"]
        await analyze_command(update, context)
    elif "eth" in user_input_lower or "以太坊" in user_input_lower:
        context.args = ["ETH"]
        await analyze_command(update, context)
    elif "sol" in user_input_lower:
        context.args = ["SOL"]
        await analyze_command(update, context)
    elif "top" in user_input_lower or "热门" in user_input_lower:
        await top_command(update, context)
    elif "portfolio" in user_input_lower or "仓位" in user_input_lower:
        await portfolio_command(update, context)
    else:
        await update.message.reply_text(
            "🤖 收到消息！\n\n"
            "可用命令:\n"
            "/analyze BTC - 市场分析\n"
            "/trade SOL - 交易计划\n"
            "/top - 热门代币\n"
            "/portfolio - 仓位\n\n"
            "💡 也可直接输入币种名称"
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    print(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ 发生错误，请重试")

def main():
    """Start the bot"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ 请设置 TELEGRAM_BOT_TOKEN 环境变量")
        return
    
    print(f"🤖 Starting Telegram Bot...")
    
    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("balance", balance_command))
    app.add_handler(CommandHandler("analyze", analyze_command))
    app.add_handler(CommandHandler("token", token_command))
    app.add_handler(CommandHandler("trade", trade_command))
    app.add_handler(CommandHandler("top", top_command))
    app.add_handler(CommandHandler("funds", funds_command))
    app.add_handler(CommandHandler("connect", connect_command))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    app.add_error_handler(error_handler)
    
    # Start polling
    print("✅ Bot is running! Press Ctrl+C to stop")
    app.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()
