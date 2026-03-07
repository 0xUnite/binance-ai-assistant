"""
Binance AI API Server
REST API for all Binance data
"""
import os
import sys
from flask import Flask, jsonify, request

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from indicators.indicators import analyze_market, calculate_rsi, calculate_macd
from utils.binance_api import (
    get_price, get_24h_ticker, get_klines, get_depth,
    get_funding_rate, get_top_coins, get_account_balance,
    get_announcements, get_all_prices
)

app = Flask(__name__)

# Configuration
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_SECRET_KEY", "")

# ============ Market Data Endpoints ============

@app.route('/api/price/<symbol>', methods=['GET'])
def price(symbol):
    """Get current price"""
    try:
        price = get_price(symbol)
        return jsonify({"symbol": symbol.upper(), "price": price})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/ticker/<symbol>', methods=['GET'])
def ticker(symbol):
    """Get 24h ticker"""
    try:
        data = get_24h_ticker(symbol)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/klines', methods=['GET'])
def klines():
    """Get kline/candlestick data"""
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', '1h')
    limit = int(request.args.get('limit', 100))
    
    try:
        data = get_klines(symbol, interval, limit)
        return jsonify({"symbol": symbol.upper(), "interval": interval, "data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/depth/<symbol>', methods=['GET'])
def depth(symbol):
    """Get order book depth"""
    limit = int(request.args.get('limit', 20))
    try:
        data = get_depth(symbol, limit)
        return jsonify({"symbol": symbol.upper(), "depth": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/trades/<symbol>', methods=['GET'])
def trades(symbol):
    """Get recent trades"""
    limit = int(request.args.get('limit', 20))
    from utils.binance_api import get_recent_trades
    try:
        data = get_recent_trades(symbol, limit)
        return jsonify({"symbol": symbol.upper(), "trades": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/funding/<symbol>', methods=['GET'])
def funding(symbol):
    """Get funding rate"""
    try:
        data = get_funding_rate(symbol)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============ Analysis Endpoints ============

@app.route('/api/analysis/<symbol>', methods=['GET'])
def analysis(symbol):
    """Get technical analysis"""
    interval = request.args.get('interval', '1h')
    
    try:
        klines = get_klines(symbol, interval, 100)
        prices = [k["close"] for k in klines]
        volumes = [k["volume"] for k in klines]
        
        result = analyze_market(prices, volumes)
        result["symbol"] = symbol.upper()
        result["interval"] = interval
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/rsi/<symbol>', methods=['GET'])
def rsi(symbol):
    """Get RSI indicator"""
    interval = request.args.get('interval', '1h')
    period = int(request.args.get('period', 14))
    
    try:
        klines = get_klines(symbol, interval, period + 20)
        prices = [k["close"] for k in klines]
        rsi_value = calculate_rsi(prices, period)
        
        return jsonify({
            "symbol": symbol.upper(),
            "interval": interval,
            "period": period,
            "rsi": rsi_value
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/macd/<symbol>', methods=['GET'])
def macd(symbol):
    """Get MACD indicator"""
    interval = request.args.get('interval', '1h')
    
    try:
        klines = get_klines(symbol, interval, 50)
        prices = [k["close"] for k in klines]
        macd_data = calculate_macd(prices)
        
        return jsonify({
            "symbol": symbol.upper(),
            "interval": interval,
            **macd_data
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============ Market Endpoints ============

@app.route('/api/top', methods=['GET'])
def top():
    """Get top coins by volume"""
    limit = int(request.args.get('limit', 10))
    try:
        data = get_top_coins(limit)
        return jsonify({"data": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/prices', methods=['GET'])
def prices():
    """Get all USDT prices"""
    try:
        data = get_all_prices()
        return jsonify({"count": len(data), "prices": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============ Account Endpoints ============

@app.route('/api/balance', methods=['GET'])
def balance():
    """Get account balance"""
    try:
        data = get_account_balance()
        if not data:
            return jsonify({"error": "API key not configured"}), 401
        return jsonify({"balances": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============ News Endpoints ============

@app.route('/api/news', methods=['GET'])
def news():
    """Get latest announcements"""
    try:
        data = get_announcements()
        return jsonify({"news": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ============ Utility Endpoints ============

@app.route('/api/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "ok",
        "version": "3.0.0",
        "api_key_configured": bool(API_KEY and API_SECRET)
    })

@app.route('/', methods=['GET'])
def index():
    """API index"""
    return jsonify({
        "name": "Binance AI Assistant API",
        "version": "3.0.0",
        "endpoints": {
            "market": ["/api/price/<symbol>", "/api/ticker/<symbol>", "/api/klines", "/api/depth/<symbol>"],
            "analysis": ["/api/analysis/<symbol>", "/api/rsi/<symbol>", "/api/macd/<symbol>"],
            "market_data": ["/api/top", "/api/prices"],
            "account": ["/api/balance"],
            "news": ["/api/news"],
            "utility": ["/api/health"]
        }
    })

def main():
    """Start the API server"""
    port = int(os.getenv("PORT", 3000))
    print(f"🚀 Starting Binance AI API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
