"""
Technical Indicators Library
RSI, MACD, MA, Bollinger Bands, etc.
"""
import math
from typing import List, Tuple, Dict

def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate RSI indicator"""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return round(rsi, 2)

def calculate_ema(prices: List[float], period: int) -> float:
    """Calculate EMA (Exponential Moving Average)"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return round(ema, 2)

def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
    """Calculate MACD indicator"""
    if len(prices) < slow + signal:
        return {"macd": 0, "signal": 0, "histogram": 0}
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    
    # Signal line (simplified)
    signal_line = macd_line * 0.9  # Simplified signal
    
    histogram = macd_line - signal_line
    
    return {
        "macd": round(macd_line, 2),
        "signal": round(signal_line, 2),
        "histogram": round(histogram, 2)
    }

def calculate_ma(prices: List[float], period: int) -> float:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return prices[-1] if prices else 0
    return round(sum(prices[-period:]) / period, 2)

def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return {"upper": 0, "middle": 0, "lower": 0}
    
    ma = calculate_ma(prices, period)
    variance = sum((p - ma) ** 2 for p in prices[-period:]) / period
    std = math.sqrt(variance)
    
    return {
        "upper": round(ma + std_dev * std, 2),
        "middle": round(ma, 2),
        "lower": round(ma - std_dev * std, 2)
    }

def calculate_volume_ma(volumes: List[float], period: int = 20) -> float:
    """Calculate Volume Moving Average"""
    if len(volumes) < period:
        return volumes[-1] if volumes else 0
    return round(sum(volumes[-period:]) / period, 2)

def get_trend(prices: List[float], period: int = 20) -> str:
    """Determine price trend"""
    if len(prices) < period:
        return "震荡"
    
    ma_short = calculate_ma(prices, 5)
    ma_long = calculate_ma(prices, period)
    
    if ma_short > ma_long * 1.02:
        return "上涨"
    elif ma_short < ma_long * 0.98:
        return "下跌"
    return "震荡"

def get_market_signal(rsi: float, macd: Dict, trend: str) -> Tuple[str, str]:
    """Generate trading signal based on indicators"""
    signals = []
    strength = 0
    
    # RSI signals
    if rsi < 30:
        signals.append("RSI超卖")
        strength -= 1
    elif rsi > 70:
        signals.append("RSI超买")
        strength += 1
    
    # MACD signals
    if macd["histogram"] > 0 and macd["macd"] > macd["signal"]:
        signals.append("MACD金叉")
        strength -= 0.5
    elif macd["histogram"] < 0 and macd["macd"] < macd["signal"]:
        signals.append("MACD死叉")
        strength += 0.5
    
    # Trend signals
    if trend == "上涨":
        signals.append("趋势向上")
        strength -= 0.5
    elif trend == "下跌":
        signals.append("趋势向下")
        strength += 0.5
    
    # Overall signal
    if strength <= -1:
        signal = "买入"
    elif strength >= 1:
        signal = "卖出"
    else:
        signal = "观望"
    
    return signal, ",".join(signals) if signals else "无明显信号"

def analyze_market(prices: List[float], volumes: List[float] = None) -> Dict:
    """Complete market analysis"""
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    ma20 = calculate_ma(prices, 20)
    ma50 = calculate_ma(prices, 50) if len(prices) >= 50 else None
    trend = get_trend(prices)
    signal, reasons = get_market_signal(rsi, macd, trend)
    
    bb = calculate_bollinger_bands(prices)
    
    result = {
        "current_price": prices[-1] if prices else 0,
        "rsi": rsi,
        "macd": macd,
        "ma20": ma20,
        "ma50": ma50,
        "bollinger_bands": bb,
        "trend": trend,
        "signal": signal,
        "reasons": reasons
    }
    
    if volumes:
        result["volume_ma"] = calculate_volume_ma(volumes)
        result["volume_ratio"] = round(volumes[-1] / result["volume_ma"], 2) if result["volume_ma"] > 0 else 1
    
    return result
