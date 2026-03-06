"""
AI Helper - 使用 OpenClaw 内置 AI
不需要额外 API Key，直接通过 Agent 调用
"""

def ask_ai(prompt: str, context: str = "") -> str:
    """
    使用 OpenClaw AI 回答问题
    在 OpenClaw 环境中可以直接调用
    
    示例:
    result = ask_ai("分析 BTC 走势", "当前价格 70000，RSI 65")
    """
    # 这个文件在 OpenClaw 环境中会被替换为实际 AI 调用
    # 本地测试时返回模拟响应
    return f"[AI Response] {prompt}"

def generate_trading_idea(symbol: str, data: dict) -> str:
    """生成交易建议"""
    return f"""
{symbol} 交易分析:

1. 技术面: {'偏多' if data.get('rsi', 50) < 60 else '偏空'}
2. RSI: {data.get('rsi', 'N/A')}
3. 趋势: {data.get('trend', '震荡')}

建议: {'观望' if data.get('rsi', 50) > 70 else '可以关注'}
⚠️ 仅供参考，不构成投资建议
"""

def generate_post_content(symbol: str, data: dict) -> str:
    """生成推文内容"""
    price = data.get('price', 0)
    change = data.get('change_24h', 0)
    
    emoji = "🚀" if change > 3 else "📈" if change > 0 else "📉"
    
    return f"""
{emoji} {symbol} 实时分析

💰 当前: ${price:,.2f}
📈 24h: {change:+.2f}%

#Crypto #{symbol}
"""

