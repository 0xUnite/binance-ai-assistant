"""
Binance AI Assistant Web Dashboard
Modern UI with real-time data visualization
"""
import os
from flask import Flask, render_template_string, jsonify, request
from indicators.indicators import analyze_market
from utils.binance_api import (
    get_price, get_24h_ticker, get_klines, get_top_coins,
    get_account_balance, get_all_prices
)
from utils.whale_tracker import get_open_interest, get_market_sentiment, get_liquidation_clusters
from utils.position_tracker import PositionTracker
from utils.post_generator import generate_post_basic

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binance Market Pulse AI</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
        }
        .header {
            background: rgba(0,0,0,0.3);
            padding: 20px;
            border-bottom: 1px solid #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 24px; color: #f0b90b; }
        .nav { display: flex; gap: 20px; }
        .nav a { color: #888; text-decoration: none; transition: 0.3s; }
        .nav a:hover, .nav a.active { color: #f0b90b; }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .card h3 { color: #888; font-size: 14px; margin-bottom: 10px; }
        .card .value { font-size: 28px; font-weight: bold; }
        .card .change { font-size: 14px; }
        .green { color: #00c087; }
        .red { color: #f6465d; }
        
        .price-display { font-size: 42px; font-weight: bold; }
        
        .chart-container { height: 300px; margin-top: 20px; }
        
        .btn {
            background: #f0b90b;
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            transition: 0.3s;
        }
        .btn:hover { background: #d49b0a; }
        .btn-outline {
            background: transparent;
            border: 1px solid #f0b90b;
            color: #f0b90b;
        }
        
        .signal-buy { background: rgba(0,192,135,0.2); border: 1px solid #00c087; }
        .signal-sell { background: rgba(246,70,93,0.2); border: 1px solid #f6465d; }
        .signal-neutral { background: rgba(136,136,136,0.2); border: 1px solid #888; }
        
        .signal-badge {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
        }
        
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #888; font-weight: normal; }
        
        .whale-alert {
            background: linear-gradient(90deg, rgba(240,185,11,0.1), transparent);
            border-left: 3px solid #f0b90b;
            padding: 10px;
            margin: 5px 0;
        }
        
        .tabs { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab {
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            cursor: pointer;
        }
        .tab.active { background: #f0b90b; color: #000; }
        
        .post-preview {
            background: #000;
            padding: 20px;
            border-radius: 12px;
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Binance Market Pulse AI</h1>
        <nav class="nav">
            <a href="#" class="active" onclick="showPage('dashboard')">仪表盘</a>
            <a href="#" onclick="showPage('analysis')">分析</a>
            <a href="#" onclick="showPage('whales')">巨鲸</a>
            <a href="#" onclick="showPage('trade')">交易</a>
            <a href="#" onclick="showPage('post')">发推</a>
        </nav>
    </div>
    
    <div class="container" id="content">
        <!-- Content loaded dynamically -->
    </div>
    
    <script>
        let currentPage = 'dashboard';
        
        async function loadPage(page) {
            const content = document.getElementById('content');
            currentPage = page;
            
            if (page === 'dashboard') {
                const resp = await fetch('/api/dashboard');
                const data = await resp.json();
                
                content.innerHTML = `
                    <div class="grid">
                        <div class="card">
                            <h3>BTC 价格</h3>
                            <div class="price-display">$${data.btc.price.toLocaleString()}</div>
                            <div class="change ${data.btc.change >= 0 ? 'green' : 'red'}">
                                ${data.btc.change >= 0 ? '▲' : '▼'} ${Math.abs(data.btc.change).toFixed(2)}%
                            </div>
                        </div>
                        <div class="card">
                            <h3>ETH 价格</h3>
                            <div class="price-display">$${data.eth.price.toLocaleString()}</div>
                            <div class="change ${data.eth.change >= 0 ? 'green' : 'red'}">
                                ${data.eth.change >= 0 ? '▲' : '▼'} ${Math.abs(data.eth.change).toFixed(2)}%
                            </div>
                        </div>
                        <div class="card">
                            <h3>市场情绪</h3>
                            <div class="value">${data.sentiment}</div>
                        </div>
                        <div class="card">
                            <h3>BTC 合约持仓 (OI)</h3>
                            <div class="value">$${(data.btc_oi/1e9).toFixed(1)}B</div>
                            <div class="change ${data.btc_oi_change >= 0 ? 'green' : 'red'}">
                                ${data.btc_oi_change >= 0 ? '▲' : '▼'} ${Math.abs(data.btc_oi_change).toFixed(1)}%
                            </div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <h3>BTC/USDT K线</h3>
                        <div class="chart-container">
                            <canvas id="priceChart"></canvas>
                        </div>
                    </div>
                    
                    <div class="grid" style="margin-top: 20px;">
                        <div class="card">
                            <h3>热门代币</h3>
                            <table>
                                <tr><th>排名</th><th>代币</th><th>价格</th><th>24h</th></tr>
                                ${data.top_coins.map((c, i) => `
                                    <tr>
                                        <td>${i+1}</td>
                                        <td>${c.symbol}</td>
                                        <td>$${c.price.toFixed(2)}</td>
                                        <td class="${c.change >= 0 ? 'green' : 'red'}">${c.change >= 0 ? '+' : ''}${c.change.toFixed(1)}%</td>
                                    </tr>
                                `).join('')}
                            </table>
                        </div>
                        <div class="card">
                            <h3>技术信号 (BTC)</h3>
                            <div class="signal-${data.btc_signal.toLowerCase()}">
                                <span class="signal-badge">${data.btc_signal}</span>
                                <p style="margin-top: 10px; color: #888;">${data.btc_reasons}</p>
                            </div>
                            <div style="margin-top: 20px;">
                                <p>RSI: ${data.btc_rsi}</p>
                                <p>趋势: ${data.btc_trend}</p>
                                <p>MA20: $${data.btc_ma20.toLocaleString()}</p>
                            </div>
                        </div>
                    </div>
                `;
                
                // Load chart
                const chartResp = await fetch('/api/chart/btc');
                const chartData = await chartResp.json();
                
                new Chart(document.getElementById('priceChart'), {
                    type: 'line',
                    data: {
                        labels: chartData.labels,
                        datasets: [{
                            label: 'BTC Price',
                            data: chartData.prices,
                            borderColor: '#f0b90b',
                            backgroundColor: 'rgba(240,185,11,0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            x: { grid: { color: '#333' } },
                            y: { grid: { color: '#333' } }
                        }
                    }
                });
            }
            
            // Update nav
            document.querySelectorAll('.nav a').forEach(a => a.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        // Initialize
        loadPage('dashboard');
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/dashboard')
def dashboard_data():
    """Get all dashboard data"""
    # Get BTC data
    btc_ticker = get_24h_ticker("BTCUSDT")
    btc_klines = get_klines("BTCUSDT", "1h", 50)
    btc_prices = [k["close"] for k in btc_klines]
    btc_analysis = analyze_market(btc_prices)
    
    # Get ETH data
    eth_ticker = get_24h_ticker("ETHUSDT")
    
    # Get top coins
    top = get_top_coins(5)
    
    # Get OI data
    btc_oi = get_open_interest("BTC")
    
    # Get sentiment
    sentiment = get_market_sentiment("BTC")
    
    return jsonify({
        "btc": {
            "price": btc_ticker["price"],
            "change": btc_ticker["change_24h"]
        },
        "eth": {
            "price": eth_ticker["price"],
            "change": eth_ticker["change_24h"]
        },
        "sentiment": sentiment,
        "btc_oi": btc_oi.get("open_interest", 0),
        "btc_oi_change": btc_oi.get("change_24h", 0),
        "top_coins": top,
        "btc_signal": btc_analysis.get("signal", "观望"),
        "btc_reasons": btc_analysis.get("reasons", ""),
        "btc_rsi": btc_analysis.get("rsi", 50),
        "btc_trend": btc_analysis.get("trend", "震荡"),
        "btc_ma20": btc_analysis.get("ma20", 0)
    })

@app.route('/api/chart/<symbol>')
def chart_data(symbol):
    """Get chart data"""
    klines = get_klines(f"{symbol}USDT", "1h", 50)
    
    labels = []
    prices = []
    
    for k in klines:
        from datetime import datetime
        dt = datetime.fromtimestamp(k["open_time"]/1000)
        labels.append(dt.strftime("%H:%M"))
        prices.append(k["close"])
    
    return jsonify({"labels": labels, "prices": prices})

@app.route('/api/analyze/<symbol>')
def analyze(symbol):
    """Get full analysis"""
    try:
        ticker = get_24h_ticker(f"{symbol}USDT")
        klines = get_klines(f"{symbol}USDT", "1h", 100)
        prices = [k["close"] for k in klines]
        volumes = [k["volume"] for k in klines]
        
        analysis = analyze_market(prices, volumes)
        
        oi = get_open_interest(symbol)
        liquidation = get_liquidation_clusters(symbol)
        
        return jsonify({
            "ticker": ticker,
            "analysis": analysis,
            "oi": oi,
            "liquidation": liquidation
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/generate-post/<symbol>')
def generate_post(symbol):
    """Generate post for symbol"""
    try:
        from utils.post_generator import generate_post_basic
        post = generate_post_basic(symbol)
        return jsonify({"post": post})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def main():
    port = int(os.getenv("PORT", 3000))
    print(f"🌐 Starting Web Dashboard on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    main()
