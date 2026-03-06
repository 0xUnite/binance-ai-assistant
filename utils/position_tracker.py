"""
Position Tracker
Track open positions, P&L, and trade history
"""
import time
import json
from typing import List, Dict
from datetime import datetime

class Position:
    """Position class"""
    def __init__(self, symbol: str, entry_price: float, quantity: float, leverage: int = 1):
        self.symbol = symbol
        self.entry_price = entry_price
        self.quantity = quantity
        self.leverage = leverage
        self.entry_time = datetime.now()
        self.stop_loss = None
        self.take_profit = None
        self.orders = []  # DCA orders
    
    def to_dict(self) -> Dict:
        return {
            "symbol": self.symbol,
            "entry_price": self.entry_price,
            "quantity": self.quantity,
            "leverage": self.leverage,
            "entry_time": self.entry_time.isoformat(),
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit,
            "orders": self.orders
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        pos = cls(data["symbol"], data["entry_price"], data["quantity"], data["leverage"])
        pos.stop_loss = data.get("stop_loss")
        pos.take_profit = data.get("take_profit")
        pos.orders = data.get("orders", [])
        return pos


class PositionTracker:
    """Track user positions and P&L"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.positions: List[Position] = []
        self.closed_trades: List[Dict] = []
        self.total_pnl = 0
    
    def open_position(self, symbol: str, entry_price: float, quantity: float, 
                      leverage: int = 1, stop_loss: float = None, take_profit: float = None):
        """Open a new position"""
        pos = Position(symbol, entry_price, quantity, leverage)
        pos.stop_loss = stop_loss
        pos.take_profit = take_profit
        
        self.positions.append(pos)
        return pos
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "manual"):
        """Close a position"""
        for i, pos in enumerate(self.positions):
            if pos.symbol == symbol:
                # Calculate P&L
                pnl = self._calculate_pnl(pos, exit_price)
                
                # Record closed trade
                trade = {
                    "symbol": pos.symbol,
                    "entry_price": pos.entry_price,
                    "exit_price": exit_price,
                    "quantity": pos.quantity,
                    "leverage": pos.leverage,
                    "pnl": pnl,
                    "pnl_percent": (exit_price - pos.entry_price) / pos.entry_price * 100 * pos.leverage,
                    "entry_time": pos.entry_time.isoformat(),
                    "exit_time": datetime.now().isoformat(),
                    "reason": reason
                }
                
                self.closed_trades.append(trade)
                self.total_pnl += pnl
                
                # Remove position
                self.positions.pop(i)
                
                return trade
        
        return None
    
    def _calculate_pnl(self, position: Position, current_price: float) -> float:
        """Calculate P&L for a position"""
        if position.symbol.endswith("USDT"):
            # Long position
            pnl = (current_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - current_price) * position.quantity
        
        return pnl * position.leverage
    
    def get_positions_summary(self, prices: Dict) -> str:
        """Get positions summary with current prices"""
        if not self.positions:
            return "📊 暂无持仓"
        
        msg = "📊 *当前持仓*\n\n"
        
        total_pnl = 0
        total_value = 0
        
        for pos in self.positions:
            current_price = prices.get(pos.symbol, pos.entry_price)
            pnl = self._calculate_pnl(pos, current_price)
            pnl_percent = (current_price - pos.entry_price) / pos.entry_price * 100 * pos.leverage
            
            total_pnl += pnl
            total_value += current_price * pos.quantity
            
            emoji = "🟢" if pnl >= 0 else "🔴"
            
            msg += f"{emoji} *{pos.symbol}*\n"
            msg += f"   数量: {pos.quantity}\n"
            msg += f"   杠杆: {pos.leverage}x\n"
            msg += f"   入场: ${pos.entry_price:,.2f}\n"
            msg += f"   当前: ${current_price:,.2f}\n"
            msg += f"   盈亏: ${pnl:+.2f} ({pnl_percent:+.2f}%)\n"
            
            if pos.stop_loss:
                msg += f"   止损: ${pos.stop_loss:,.2f}\n"
            if pos.take_profit:
                msg += f"   止盈: ${pos.take_profit:,.2f}\n"
            
            msg += "\n"
        
        total_pnl_percent = (total_pnl / (total_value - total_pnl) * 100) if total_value > total_pnl else 0
        
        msg += f"💰 总盈亏: ${total_pnl:+.2f} ({total_pnl_percent:+.2f}%)"
        
        return msg
    
    def get_closed_trades_summary(self, limit: int = 10) -> str:
        """Get closed trades summary"""
        if not self.closed_trades:
            return "📊 暂无平仓记录"
        
        trades = self.closed_trades[-limit:]
        
        msg = f"📊 *历史交易 (最近{len(trades)}笔)*\n\n"
        
        wins = 0
        losses = 0
        total_pnl = 0
        
        for trade in reversed(trades):
            pnl = trade["pnl"]
            total_pnl += pnl
            
            if pnl > 0:
                wins += 1
                emoji = "🟢"
            else:
                losses += 1
                emoji = "🔴"
            
            msg += f"{emoji} {trade['symbol']}\n"
            msg += f"   入: ${trade['entry_price']:,.2f} → 出: ${trade['exit_price']:,.2f}\n"
            msg += f"   盈亏: ${pnl:+.2f} ({trade['pnl_percent']:+.2f}%)\n"
            msg += f"   原因: {trade['reason']}\n\n"
        
        win_rate = (wins / (wins + losses) * 100) if (wins + losses) > 0 else 0
        
        msg += f"📈 胜率: {win_rate:.1f}% ({wins}胜 {losses}负)\n"
        msg += f"💰 总盈亏: ${total_pnl:+.2f}"
        
        return msg
    
    def save_to_file(self, filepath: str):
        """Save positions to file"""
        data = {
            "user_id": self.user_id,
            "positions": [p.to_dict() for p in self.positions],
            "closed_trades": self.closed_trades,
            "total_pnl": self.total_pnl
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load_from_file(cls, user_id: str, filepath: str) -> 'PositionTracker':
        """Load positions from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            tracker = cls(user_id)
            tracker.positions = [Position.from_dict(p) for p in data.get("positions", [])]
            tracker.closed_trades = data.get("closed_trades", [])
            tracker.total_pnl = data.get("total_pnl", 0)
            
            return tracker
        except:
            return cls(user_id)


def simulate_position_example():
    """Simulate position tracking example"""
    # Simulate prices
    prices = {
        "BTCUSDT": 70000,
        "ETHUSDT": 3500,
        "SOLUSDT": 120
    }
    
    # Create tracker
    tracker = PositionTracker("test_user")
    
    # Open some positions
    tracker.open_position("BTCUSDT", 68000, 0.1, leverage=3, stop_loss=65000, take_profit=75000)
    tracker.open_position("ETHUSDT", 3400, 1.0, leverage=2, stop_loss=3200, take_profit=3800)
    
    # Simulate price changes
    prices["BTCUSDT"] = 71000  # +4.4% -> +13.2% with 3x
    prices["ETHUSDT"] = 3300   # -2.9% -> -5.8% with 2x
    
    # Print summary
    print(tracker.get_positions_summary(prices))
    
    # Close a position
    trade = tracker.close_position("BTCUSDT", 71000, "take_profit")
    print(f"\n平仓BTC，盈亏: ${trade['pnl']:+.2f}")
    
    # Print closed trades
    print("\n" + tracker.get_closed_trades_summary())


if __name__ == "__main__":
    simulate_position_example()
