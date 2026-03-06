"""
Social Trading - 社交交易/跟单
复制聪明钱/KOL/巨鲸的交易
"""
from typing import Dict, List
from datetime import datetime

class CopyTrader:
    """跟单交易器"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.following = []  # 正在跟单的交易者
        self.trades = []
        self.pnl = 0
    
    def add_signal_source(self, address: str, name: str, copy_pct: float = 100):
        """添加跟单源"""
        self.following.append({
            "address": address,
            "name": name,
            "copy_pct": copy_pct,  # 复制比例
            "enabled": True
        })
    
    def remove_signal_source(self, address: str):
        """移除跟单源"""
        self.following = [f for f in self.following if f["address"] != address]
    
    def simulate_copy_trade(self, signal: Dict) -> Dict:
        """
        模拟跟单交易
        signal = {
            "token": "SOL",
            "action": "BUY",
            "amount": 25000,  # USDT
            "source": "Smart Money",
            "wallet": "7x..."
        }
        """
        # 模拟跟单结果
        result = {
            "signal": signal,
            "copied": True,
            "amount": signal["amount"],
            "entry_price": self._get_price(signal["token"]),
            "time": datetime.now().isoformat()
        }
        
        self.trades.append(result)
        
        return result
    
    def _get_price(self, token: str) -> float:
        """获取价格（模拟）"""
        prices = {"BTC": 70000, "ETH": 3500, "SOL": 120, "BNB": 600}
        return prices.get(token, 100)
    
    def get_following_list(self) -> str:
        """获取跟单列表"""
        if not self.following:
            return "暂无跟单源"
        
        msg = "📋 *正在跟单:*\n\n"
        
        for f in self.following:
            status = "✅" if f["enabled"] else "⏸️"
            msg += f"{status} {f['name']}\n"
            msg += f"   地址: {f['address'][:10]}...\n"
            msg += f"   复制比例: {f['copy_pct']}%\n\n"
        
        return msg
    
    def get_trade_history(self, limit: int = 10) -> str:
        """获取跟单历史"""
        if not self.trades:
            return "暂无跟单记录"
        
        msg = "📊 *跟单记录*\n\n"
        
        for t in self.trades[-limit:]:
            token = t["signal"]["token"]
            action = t["signal"]["action"]
            source = t["signal"]["source"]
            
            emoji = "🟢" if action == "BUY" else "🔴"
            
            msg += f"{emoji} {action} {token}\n"
            msg += f"   来源: {source}\n"
            msg += f"   金额: ${t['amount']:,.0f}\n"
            msg += f"   时间: {t['time'][:10]}\n\n"
        
        return msg


def get_smart_money_signals(chain: str = "solana") -> List[Dict]:
    """
    获取 Smart Money 信号
    模拟数据 - 实际需要连接链上数据源
    """
    signals = [
        {
            "chain": "solana",
            "token": "DEEP",
            "action": "BUY",
            "amount": 25000,
            "source": "Smart Money",
            "wallet": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
            "tx_hash": "5x7P9k...",
            "time": "2 min ago",
            "confidence": 85
        },
        {
            "chain": "solana",
            "token": "DRGON",
            "action": "BUY",
            "amount": 15000,
            "source": "Whale",
            "wallet": "9xQeWvG816bVc9AAQqn3HPg7uHQ5r7Y3r",
            "tx_hash": "3k9M2n...",
            "time": "5 min ago",
            "confidence": 72
        },
        {
            "chain": "base",
            "token": "DEGEN",
            "action": "BUY",
            "amount": 8000,
            "source": "KOL",
            "wallet": "0x1234...abcd",
            "tx_hash": "0x8f2...",
            "time": "12 min ago",
            "confidence": 65
        }
    ]
    
    return [s for s in signals if s["chain"] == chain]


def scan_and_copy(chain: str = "solana", min_amount: int = 5000) -> str:
    """
    扫描信号并自动跟单
    """
    signals = get_smart_money_signals(chain)
    
    if not signals:
        return "❌ 暂无信号"
    
    # 过滤金额
    filtered = [s for s in signals if s["amount"] >= min_amount]
    
    if not filtered:
        return f"❌ 没有超过 ${min_amount} 的信号"
    
    msg = f"🐋 *{chain.upper()} 信号发现*\n\n"
    
    for s in filtered:
        emoji = "🟢"
        source_emoji = {"Smart Money": "🧠", "Whale": "🐋", "KOL": "📢"}.get(s["source"], "📊")
        
        msg += f"{source_emoji} *{s['source']}*\n"
        msg += f"   代币: {s['token']}\n"
        msg += f"   {emoji} {s['action']} ${s['amount']:,}\n"
        msg += f"   置信度: {s['confidence']}%\n"
        msg += f"   时间: {s['time']}\n\n"
    
    msg += "💡 输入 /copy [代币] 执行跟单"
    
    return msg


if __name__ == "__main__":
    # 测试
    print(scan_and_copy("solana"))
    print("\n" + "="*50 + "\n")
    
    trader = CopyTrader("user123")
    trader.add_signal_source("7xKXtg2CW...", "Smart Money Whale", 50)
    print(trader.get_following_list())
