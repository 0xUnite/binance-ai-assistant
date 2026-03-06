"""
Backtesting Engine
Test trading strategies on historical data
"""
import json
from typing import List, Dict, Tuple
from datetime import datetime
from utils.binance_api import get_klines

class Backtest:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.position = 0
        self.position_entry = 0
        self.trades = []
        self.equity_curve = []
    
    def buy(self, price: float, quantity: float, timestamp: int):
        """Execute buy order"""
        cost = price * quantity
        
        if cost > self.capital:
            # Adjust quantity to available capital
            quantity = self.capital / price
            cost = price * quantity
        
        self.capital -= cost
        self.position += quantity
        self.position_entry = price
        
        self.trades.append({
            "type": "BUY",
            "price": price,
            "quantity": quantity,
            "value": cost,
            "timestamp": timestamp,
            "pnl": 0
        })
    
    def sell(self, price: float, quantity: float = None, timestamp: int = 0):
        """Execute sell order"""
        if self.position == 0:
            return None
        
        sell_qty = quantity if quantity else self.position
        sell_qty = min(sell_qty, self.position)
        
        proceeds = price * sell_qty
        pnl = (price - self.position_entry) * sell_qty
        
        self.capital += proceeds
        self.position -= sell_qty
        
        self.trades.append({
            "type": "SELL",
            "price": price,
            "quantity": sell_qty,
            "value": proceeds,
            "timestamp": timestamp,
            "pnl": pnl
        })
        
        if self.position == 0:
            self.position_entry = 0
        
        return pnl
    
    def get_equity(self, current_price: float) -> float:
        """Get current equity"""
        return self.capital + (self.position * current_price)
    
    def run_rsi_strategy(self, symbol: str, rsi_oversold: float = 30, 
                        rsi_overbought: float = 70, quantity_pct: float = 0.1) -> Dict:
        """Run RSI strategy backtest"""
        # Get historical data
        klines = get_klines(symbol, "1h", 500)
        
        if not klines:
            return {"error": "No data available"}
        
        # Calculate RSI
        prices = [k["close"] for k in klines]
        timestamps = [k["open_time"] for k in klines]
        
        # Reset
        self.__init__(self.initial_capital)
        
        # Track RSI
        rsi_values = []
        
        for i in range(14, len(prices)):
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
            
            rsi_values.append(rsi)
            
            current_price = prices[i]
            current_rsi = rsi
            timestamp = timestamps[i]
            
            # Record equity
            equity = self.get_equity(current_price)
            self.equity_curve.append({
                "timestamp": timestamp,
                "equity": equity,
                "price": current_price,
                "rsi": current_rsi
            })
            
            # Trading logic
            if current_rsi < rsi_oversold and self.position == 0:
                # Buy signal
                buy_qty = (self.capital * quantity_pct) / current_price
                self.buy(current_price, buy_qty, timestamp)
                
            elif current_rsi > rsi_overbought and self.position > 0:
                # Sell signal
                self.sell(current_price, timestamp=timestamp)
        
        # Close any remaining position
        if self.position > 0:
            self.sell(prices[-1], timestamp=timestamps[-1])
        
        return self._generate_report(symbol, "RSI Strategy")
    
    def run_ma_crossover_strategy(self, symbol: str, fast_ma: int = 10, 
                                  slow_ma: int = 50, quantity_pct: float = 0.1) -> Dict:
        """Run Moving Average crossover strategy"""
        klines = get_klines(symbol, "1h", 500)
        
        if not klines:
            return {"error": "No data available"}
        
        prices = [k["close"] for k in klines]
        timestamps = [k["open_time"] for k in klines]
        
        self.__init__(self.initial_capital)
        
        for i in range(slow_ma, len(prices)):
            # Calculate MAs
            fast_ma_val = sum(prices[i-fast_ma:i]) / fast_ma
            slow_ma_val = sum(prices[i-slow_ma:i]) / slow_ma
            
            prev_fast = sum(prices[i-fast_ma-1:i-1]) / fast_ma
            prev_slow = sum(prices[i-slow_ma-1:i-1]) / slow_ma
            
            current_price = prices[i]
            timestamp = timestamps[i]
            
            # Record equity
            equity = self.get_equity(current_price)
            self.equity_curve.append({
                "timestamp": timestamp,
                "equity": equity,
                "price": current_price
            })
            
            # Golden cross - buy
            if prev_fast <= prev_slow and fast_ma_val > slow_ma_val and self.position == 0:
                buy_qty = (self.capital * quantity_pct) / current_price
                self.buy(current_price, buy_qty, timestamp)
            
            # Death cross - sell
            elif prev_fast >= prev_slow and fast_ma_val < slow_ma_val and self.position > 0:
                self.sell(current_price, timestamp=timestamp)
        
        # Close position
        if self.position > 0:
            self.sell(prices[-1], timestamp=timestamps[-1])
        
        return self._generate_report(symbol, f"MA({fast_ma}/{slow_ma}) Crossover")
    
    def run_macd_strategy(self, symbol: str, quantity_pct: float = 0.1) -> Dict:
        """Run MACD strategy"""
        klines = get_klines(symbol, "1h", 500)
        
        if not klines:
            return {"error": "No data available"}
        
        prices = [k["close"] for k in klines]
        timestamps = [k["open_time"] for k in klines]
        
        self.__init__(self.initial_capital)
        
        # EMA calculation
        def calc_ema(data, period):
            multiplier = 2 / (period + 1)
            ema = sum(data[:period]) / period
            for price in data[period:]:
                ema = (price - ema) * multiplier + ema
            return ema
        
        for i in range(50, len(prices)):
            # Calculate MACD
            ema_12 = calc_ema(prices[:i+1], 12)
            ema_26 = calc_ema(prices[:i+1], 26)
            macd_line = ema_12 - ema_26
            signal_line = macd_line * 0.9  # Simplified
            
            prev_ema_12 = calc_ema(prices[:i], 12)
            prev_ema_26 = calc_ema(prices[:i], 26)
            prev_macd = prev_ema_12 - prev_ema_26
            prev_signal = prev_macd * 0.9
            
            current_price = prices[i]
            timestamp = timestamps[i]
            
            # Record equity
            equity = self.get_equity(current_price)
            self.equity_curve.append({
                "timestamp": timestamp,
                "equity": equity,
                "price": current_price
            })
            
            # MACD cross
            if prev_macd <= prev_signal and macd_line > signal_line and self.position == 0:
                buy_qty = (self.capital * quantity_pct) / current_price
                self.buy(current_price, buy_qty, timestamp)
            
            elif prev_macd >= prev_signal and macd_line < signal_line and self.position > 0:
                self.sell(current_price, timestamp=timestamp)
        
        if self.position > 0:
            self.sell(prices[-1], timestamp=timestamps[-1])
        
        return self._generate_report(symbol, "MACD Strategy")
    
    def _generate_report(self, symbol: str, strategy_name: str) -> Dict:
        """Generate backtest report"""
        final_equity = self.get_equity(prices[-1] if self.equity_curve else self.initial_capital)
        total_return = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        
        # Count trades
        buy_trades = [t for t in self.trades if t["type"] == "BUY"]
        sell_trades = [t for t in self.trades if t["type"] == "SELL"]
        
        wins = [t for t in sell_trades if t["pnl"] > 0]
        losses = [t for t in sell_trades if t["pnl"] <= 0]
        
        win_rate = (len(wins) / len(sell_trades) * 100) if sell_trades else 0
        
        total_pnl = sum(t["pnl"] for t in sell_trades)
        
        # Max drawdown
        max_equity = self.initial_capital
        max_drawdown = 0
        
        for point in self.equity_curve:
            if point["equity"] > max_equity:
                max_equity = point["equity"]
            
            drawdown = ((max_equity - point["equity"]) / max_equity) * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            "strategy": strategy_name,
            "symbol": symbol,
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "total_return": round(total_return, 2),
            "total_trades": len(sell_trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 2),
            "max_drawdown": round(max_drawdown, 2),
            "trades": self.trades[-20:]  # Last 20 trades
        }
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        print(f"\n📊 回测报告: {report['strategy']}")
        print("=" * 50)
        print(f"交易对: {report['symbol']}")
        print(f"初始资金: ${report['initial_capital']:,.2f}")
        print(f"最终资金: ${report['final_equity']:,.2f}")
        print(f"总收益率: {report['total_return']:+.2f}%")
        print(f"\n交易统计:")
        print(f"  总交易次数: {report['total_trades']}")
        print(f"  盈利交易: {report['winning_trades']}")
        print(f"  亏损交易: {report['losing_trades']}")
        print(f"  胜率: {report['win_rate']:.1f}%")
        print(f"  总盈亏: ${report['total_pnl']:+.2f}")
        print(f"  最大回撤: {report['max_drawdown']:.2f}%")
        
        if report['trades']:
            print(f"\n最近交易:")
            for t in report['trades'][-5:]:
                pnl_str = f"${t['pnl']:+.2f}" if t['type'] == 'SELL' else ""
                print(f"  {t['type']}: ${t['price']:,.2f} x {t['quantity']:.4f} {pnl_str}")


def run_comparison(symbol: str = "BTCUSDT", initial_capital: float = 10000):
    """Run and compare all strategies"""
    print(f"\n{'='*60}")
    print(f"📈 策略回测对比 - {symbol}")
    print(f"{'='*60}")
    
    backtest = Backtest(initial_capital)
    
    # RSI Strategy
    print("\n🔄 运行 RSI 策略...")
    rsi_result = backtest.run_rsi_strategy(symbol)
    backtest.print_report(rsi_result)
    
    # MA Crossover
    print("\n\n🔄 运行 MA 交叉策略...")
    ma_result = backtest.run_ma_crossover_strategy(symbol)
    backtest.print_report(ma_result)
    
    # MACD
    print("\n\n🔄 运行 MACD 策略...")
    macd_result = backtest.run_macd_strategy(symbol)
    backtest.print_report(macd_result)
    
    # Summary
    print(f"\n\n{'='*60}")
    print("📊 策略对比总结")
    print(f"{'='*60}")
    print(f"{'策略':<20} {'收益率':<12} {'胜率':<10} {'最大回撤'}")
    print("-" * 60)
    print(f"{'RSI (30/70)':<20} {rsi_result['total_return']:>+10.1f}% {rsi_result['win_rate']:>8.1f}% {rsi_result['max_drawdown']:>10.1f}%")
    print(f"{'MA(10/50) Crossover':<20} {ma_result['total_return']:>+10.1f}% {ma_result['win_rate']:>8.1f}% {ma_result['max_drawdown']:>10.1f}%")
    print(f"{'MACD':<20} {macd_result['total_return']:>+10.1f}% {macd_result['win_rate']:>8.1f}% {macd_result['max_drawdown']:>10.1f}%")


if __name__ == "__main__":
    import sys
    
    symbol = sys.argv[1] if len(sys.argv) > 1 else "BTCUSDT"
    run_comparison(symbol)
