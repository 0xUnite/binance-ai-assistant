"""
Simulation Trading (Dry-run)
Test trading strategies without real money
"""
import random
from typing import Dict, List
from datetime import datetime

class SimTrading:
    """Simulation trading engine"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.position_price = 0
        self.trades = []
        self.pnl_history = []
    
    def buy(self, symbol: str, amount: float, current_price: float) -> Dict:
        """Simulate buy order"""
        if amount > self.balance:
            return {"success": False, "error": "Insufficient balance"}
        
        self.balance -= amount
        self.position += amount / current_price
        self.position_price = current_price
        
        trade = {
            "type": "BUY",
            "symbol": symbol,
            "amount": amount,
            "price": current_price,
            "quantity": amount / current_price,
            "time": datetime.now().isoformat()
        }
        self.trades.append(trade)
        
        return {
            "success": True,
            "trade": trade,
            "balance": self.balance,
            "position": self.position
        }
    
    def sell(self, symbol: str, quantity: float, current_price: float) -> Dict:
        """Simulate sell order"""
        if quantity > self.position:
            quantity = self.position
        
        proceeds = quantity * current_price
        cost = self.position_price * quantity
        pnl = proceeds - cost
        
        self.balance += proceeds
        self.position -= quantity
        
        trade = {
            "type": "SELL",
            "symbol": symbol,
            "quantity": quantity,
            "price": current_price,
            "proceeds": proceeds,
            "pnl": pnl,
            "pnl_percent": (pnl / cost * 100) if cost > 0 else 0,
            "time": datetime.now().isoformat()
        }
        self.trades.append(trade)
        
        self.pnl_history.append(pnl)
        
        return {
            "success": True,
            "trade": trade,
            "balance": self.balance,
            "position": self.position,
            "total_pnl": sum(self.pnl_history)
        }
    
    def get_status(self, current_price: float) -> Dict:
        """Get current status"""
        unrealized_pnl = (current_price - self.position_price) * self.position if self.position > 0 else 0
        unrealized_pnl_percent = (unrealized_pnl / (self.position_price * self.position) * 100) if self.position > 0 and self.position_price > 0 else 0
        
        return {
            "balance": self.balance,
            "position": self.position,
            "entry_price": self.position_price,
            "current_price": current_price,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_percent": unrealized_pnl_percent,
            "total_pnl": sum(self.pnl_history),
            "total_return_percent": ((self.balance - self.initial_balance) / self.initial_balance) * 100
        }
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history"""
        return self.trades
    
    def reset(self):
        """Reset simulation"""
        self.balance = self.initial_balance
        self.position = 0
        self.position_price = 0
        self.trades = []
        self.pnl_history = []


def run_simulation(strategy: str = "rsi", symbol: str = "BTCUSDT", 
                   initial_balance: float = 10000, days: int = 30) -> str:
    """Run a trading simulation"""
    from utils.binance_api import get_klines
    
    # Get historical data
    klines = get_klines(symbol, "1h", days * 24)
    
    if not klines:
        return "❌ 无法获取历史数据"
    
    prices = [k["close"] for k in klines]
    
    sim = SimTrading(initial_balance)
    
    # Simple RSI strategy
    rsi_period = 14
    
    for i in range(rsi_period + 1, len(prices)):
        # Calculate RSI
        deltas = [prices[j] - prices[j-1] for j in range(i-13, i+1)]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        current_price = prices[i]
        
        # Trading logic
        if rsi < 30 and sim.position == 0:
            # Buy signal
            sim.buy(symbol, initial_balance * 0.1, current_price)
        
        elif rsi > 70 and sim.position > 0:
            # Sell signal
            sim.sell(symbol, sim.position, current_price)
    
    # Close any position
    if sim.position > 0:
        sim.sell(symbol, sim.position, prices[-1])
    
    # Generate report
    status = sim.get_status(prices[-1])
    trades = sim.get_trade_history()
    
    wins = [t for t in trades if t.get("pnl", 0) > 0]
    losses = [t for t in trades if t.get("pnl", 0) <= 0]
    
    msg = f"""
📊 *模拟交易报告*

🎯 策略: RSI (买入:RSI<30, 卖出:RSI>70)
📅 模拟周期: {days} 天
💰 初始资金: ${initial_balance:,.2f}

📈 *结果*
当前余额: ${status['balance']:,.2f}
总盈亏: ${status['total_pnl']:+.2f} ({status['total_return_percent']:+.2f}%)

📊 *交易统计*
总交易: {len(trades)}
盈利交易: {len(wins)}
亏损交易: {len(losses)}
胜率: {len(wins)/len(trades)*100:.1f}% (如果>0)

💰 *当前持仓*
状态: {'有持仓' if status['position'] > 0 else '空仓'}
数量: {status['position']:.4f}
入场价: ${status['entry_price']:,.2f}
当前价: ${status['current_price']:,.2f}
未实现盈亏: ${status['unrealized_pnl']:+.2f}

⚠️ *风险提示*: 这是模拟交易结果，不代表真实收益
"""
    
    return msg


if __name__ == "__main__":
    # Test
    print(run_simulation("rsi", "BTCUSDT", 10000, 7))
