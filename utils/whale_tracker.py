"""
Whale Activity Tracker
Monitor large transactions and whale movements
"""
import requests
import time
from typing import List, Dict

# Whale tracking APIs (free tier)
# In production, use paid services like Glassnode, Nansen, etc.

def get_whale_alerts() -> List[Dict]:
    """Get recent whale alerts (simulated)"""
    # This is a simplified version
    # In production, use APIs like:
    # - WhaleAlert.io
    # - Nansen.ai
    # - Glassnode
    
    return [
        {
            "symbol": "BTC",
            "amount": 1250,
            "type": "withdrawal",
            "from": "Binance",
            "to": "Cold Wallet",
            "value": 87500000,
            "time": "2 hours ago"
        },
        {
            "symbol": "ETH",
            "amount": 8500,
            "type": "transfer",
            "from": "Unknown",
            "to": "Kraken",
            "value": 21250000,
            "time": "4 hours ago"
        }
    ]

def get_large_transactions(symbol: str = "BTC", min_value: int = 1000000) -> List[Dict]:
    """Get large transactions above threshold"""
    # Simulated data for demo
    # In production, integrate with whale tracking APIs
    
    if symbol.upper() == "BTC":
        return [
            {
                "hash": "0x1234...5678",
                "amount": 2500,
                "value_usd": 175000000,
                "type": "withdrawal",
                "exchange": "Binance",
                "time": "1h ago"
            },
            {
                "hash": "0xabcd...efgh",
                "amount": 1200,
                "value_usd": 84000000,
                "type": "deposit",
                "exchange": "Coinbase",
                "time": "3h ago"
            }
        ]
    elif symbol.upper() == "ETH":
        return [
            {
                "hash": "0x9876...5432",
                "amount": 15000,
                "value_usd": 37500000,
                "type": "transfer",
                "from": "Binance",
                "time": "2h ago"
            }
        ]
    return []

def get_liquidation_clusters(symbol: str = "BTC") -> Dict:
    """Get liquidation price clusters"""
    # Large liquidation zones where many positions will be liquidated
    
    if symbol.upper() == "BTC":
        return {
            "symbol": "BTC",
            "long_liquidations": [
                {"price": 68000, "volume": 25000000},
                {"price": 67000, "volume": 18000000},
                {"price": 65000, "volume": 35000000}
            ],
            "short_liquidations": [
                {"price": 72000, "volume": 22000000},
                {"price": 73000, "volume": 15000000}
            ],
            "major_support": [68000, 65000, 62000],
            "major_resistance": [72000, 75000, 80000]
        }
    elif symbol.upper() == "ETH":
        return {
            "symbol": "ETH",
            "long_liquidations": [
                {"price": 3400, "volume": 8000000},
                {"price": 3200, "volume": 12000000}
            ],
            "short_liquidations": [
                {"price": 3800, "volume": 9000000}
            ],
            "major_support": [3400, 3200, 3000],
            "major_resistance": [3800, 4000, 4200]
        }
    return {}

def get_open_interest(symbol: str = "BTC") -> Dict:
    """Get Open Interest data for futures"""
    # Open Interest = total value of open positions
    # High OI = more positions = potential volatility
    
    if symbol.upper() == "BTC":
        return {
            "symbol": "BTC",
            "open_interest": 15600000000,  # $15.6B
            "change_24h": 5.2,  # +5.2%
            "long_ratio": 52.3,  # 52.3% long
            "short_ratio": 47.7,  # 47.7% short
            "funding_rate": 0.0100,  # 0.01%
            "next_funding": "4 hours",
            "sentiment": "Slightly Bullish"
        }
    elif symbol.upper() == "ETH":
        return {
            "symbol": "ETH",
            "open_interest": 8200000000,  # $8.2B
            "change_24h": 3.8,
            "long_ratio": 54.1,
            "short_ratio": 45.9,
            "funding_rate": 0.0150,
            "next_funding": "4 hours",
            "sentiment": "Bullish"
        }
    return {}

def get_funding_rate_info(symbol: str = "BTC") -> Dict:
    """Get detailed funding rate info"""
    from utils.binance_api import get_funding_rate
    
    try:
        funding = get_funding_rate(symbol)
        
        # Determine sentiment based on funding
        rate = funding.get("funding_rate", 0)
        
        if rate > 0.01:
            sentiment = "Bearish (longs paying shorts)"
        elif rate < -0.01:
            sentiment = "Bullish (shorts paying longs)"
        else:
            sentiment = "Neutral"
        
        funding["sentiment"] = sentiment
        return funding
        
    except:
        return {"error": "Not a futures symbol"}

def get_market_sentiment(symbol: str = "BTC") -> str:
    """Get overall market sentiment"""
    # Combine: funding, OI, price action, whale activity
    
    oi_data = get_open_interest(symbol)
    funding = get_funding_rate_info(symbol)
    
    bullish_signals = 0
    bearish_signals = 0
    
    # OI analysis
    if oi_data.get("change_24h", 0) > 5:
        bullish_signals += 1
    elif oi_data.get("change_24h", 0) < -5:
        bearish_signals += 1
    
    # Long/Short ratio
    if oi_data.get("long_ratio", 50) > 55:
        bullish_signals += 1
    elif oi_data.get("long_ratio", 50) < 45:
        bearish_signals += 1
    
    # Funding
    rate = funding.get("funding_rate", 0)
    if rate > 0.01:
        bearish_signals += 1
    elif rate < -0.01:
        bullish_signals += 1
    
    # Determine sentiment
    if bullish_signals > bearish_signals + 1:
        return "🟢 Strongly Bullish"
    elif bullish_signals > bearish_signals:
        return "🟢 Bullish"
    elif bearish_signals > bullish_signals + 1:
        return "🔴 Strongly Bearish"
    elif bearish_signals > bullish_signals:
        return "🔴 Bearish"
    return "⚪ Neutral"

def get_whale_report(symbol: str = "BTC") -> str:
    """Generate comprehensive whale report"""
    oi = get_open_interest(symbol)
    liquidations = get_liquidation_clusters(symbol)
    sentiment = get_market_sentiment(symbol)
    transactions = get_large_transactions(symbol)
    
    msg = f"🐋 *{symbol} 巨鲸分析*\n\n"
    
    # Open Interest
    if oi:
        msg += f"📊 *合约持仓 (OI)*\n"
        msg += f"总持仓: ${oi.get('open_interest', 0)/1e9:.1f}B\n"
        msg += f"24h变化: {oi.get('change_24h', 0):+.1f}%\n"
        msg += f"多空比: {oi.get('long_ratio', 50):.1f}% / {oi.get('short_ratio', 50):.1f}%\n"
        msg += f"资金费率: {oi.get('funding_rate', 0):.4f}%\n\n"
    
    # Sentiment
    msg += f"🎭 *市场情绪*: {sentiment}\n\n"
    
    # Liquidation zones
    if liquidations:
        msg += f"📉 *清算区域*\n"
        msg += f"主要支撑: {', '.join([f'${int(x)}' for x in liquidations.get('major_support', [])[:3]])}\n"
        msg += f"主要阻力: {', '.join([f'${int(x)}' for x in liquidations.get('major_resistance', [])[:3]])}\n\n"
    
    # Large transactions
    if transactions:
        msg += f"🔔 *大额交易*\n"
        for tx in transactions[:3]:
            msg += f"• {tx['type']}: {tx['amount']} {symbol} (${tx['value_usd']/1e6:.1f}M)\n"
    
    return msg

def main():
    """Test the whale tracker"""
    print(get_whale_report("BTC"))
    print("\n" + "="*50 + "\n")
    print(get_whale_report("ETH"))

if __name__ == "__main__":
    main()
