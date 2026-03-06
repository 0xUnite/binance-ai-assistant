"""
Binance AI Assistant Web Dashboard - Complete Version
All features in one web interface
"""
import os
from flask import Flask, render_template_string, jsonify, request
from indicators.indicators import analyze_market
from utils.binance_api import (
    get_price, get_24h_ticker, get_klines, get_top_coins,
    get_account_balance, get_all_prices
)
from utils.whale_tracker import get_open_interest, get_market_sentiment, get_liquidation_clusters
from utils.multi_chain_scanner import get_multi_chain_report
from utils.honeypot_detector import check_token_safety, scan_multiple_tokens
from utils.social_trading import scan_and_copy, get_smart_money_signals
from utils.joint_account import create_joint_account

app = Flask(__name__)

HTML = '''
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binance Market Pulse AI - Complete</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh; color: #fff; }
        .header {
            background: rgba(0,0,0,0.5); padding: 20px;
            border-bottom: 1px solid #333;
            display: flex; justify-content: space-between; align-items: center; }
        .header h1 { color: #f0b90b; }
        .nav { display: flex; gap: 15px; flex-wrap: wrap; }
        .nav a { color: #888; text-decoration: none; padding: 8px 16px; border-radius: 20px; transition: 0.3s; }
        .nav a:hover, .nav a.active { background: #f0b90b; color: #000; }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
        .card { background: rgba(255,255,255,0.05); border-radius: 16px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }
        .card h3 { color: #888; font-size: 14px; margin-bottom: 10px; }
        .value { font-size: 28px; font-weight: bold; }
        .price { font-size: 42px; font-weight: bold; }
        .green { color: #00c087; } .red { color: #f6465d; }
        .btn { background: #f0b90b; color: #000; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: bold; margin: 5px; }
        .btn:hover { background: #d49b0a; }
        .signal-buy { background: rgba(0,192,135,0.2); border: 1px solid #00c087; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .signal-sell { background: rgba(246,70,93,0.2); border: 1px solid #f6465d; padding: 15px; border-radius: 10px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        input, select { background: #333; color: #fff; border: 1px solid #555; padding: 10px; border-radius: 8px; margin: 5px; }
        .tab-container { margin-bottom: 20px; }
        .tab { padding: 10px 20px; background: rgba(255,255,255,0.05); border-radius: 8px; cursor: pointer; display: inline-block; margin-right: 10px; }
        .tab.active { background: #f0b90b; color: #000; }
        .whale-alert { background: linear-gradient(90deg, rgba(240,185,11,0.1), transparent); border-left: 3px solid #f0b90b; padding: 10px; margin: 5px 0; }
        .joint-account { background: linear-gradient(90deg, rgba(147,51,234,0.1), transparent); border: 1px solid #9333ea; padding: 15px; border-radius: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Binance Market Pulse AI</h1>
        <nav class="nav">
            <a href="#" onclick="showPage('dashboard')">仪表盘</a>
            <a href="#" onclick="showPage('analysis')">分析</a>
            <a href="#" onclick="showPage('whales')">巨鲸</a>
            <a href="#" onclick="showPage('alpha')">Alpha</a>
            <a href="#" onclick="showPage('multi')">多链</a>
            <a href="#" onclick="showPage('safety')">安全</a>
            <a href="#" onclick="showPage('copy')">跟单</a>
            <a href="#" onclick="showPage('joint')">共同账户</a>
            <a href="#" onclick="showPage('post')">发推</a>
        </nav>
    </div>
    <div class="container" id="content"></div>
    <script>
        async function loadPage(page) {
            const content = document.getElementById("content");
            content.innerHTML = "<p>加载中...</p>";
            
            if (page === "dashboard") {
                const resp = await fetch("/api/dashboard");
                const data = await resp.json();
                content.innerHTML = `
                    <div class="grid">
                        <div class="card"><h3>BTC</h3><div class="price">$${data.btc.price.toLocaleString()}</div><div class="${data.btc.change>=0?'green':'red'}">${data.btc.change>=0?'▲':'▼'} ${data.btc.change.toFixed(2)}%</div></div>
                        <div class="card"><h3>ETH</h3><div class="price">$${data.eth.price.toLocaleString()}</div><div class="${data.eth.change>=0?'green':'red'}">${data.eth.change>=0?'▲':'▼'} ${data.eth.change.toFixed(2)}%</div></div>
                        <div class="card"><h3>情绪</h3><div class="value">${data.sentiment}</div></div>
                        <div class="card"><h3>BTC OI</h3><div class="value">$${(data.btc_oi/1e9).toFixed(1)}B</div><div class="${data.btc_oi_change>=0?'green':'red'}">${data.btc_oi_change>=0?'▲':'▼'} ${data.btc_oi_change.toFixed(1)}%</div></div>
                    </div>
                    <div class="card"><h3>BTC/USDT K线</h3><canvas id="chart" height="100"></canvas></div>
                    <div class="grid" style="margin-top:20px">
                        <div class="card"><h3>热门代币</h3><table>${data.top.map((c,i)=>`<tr><td>${i+1}</td><td>${c.symbol}</td><td>$${c.price.toFixed(2)}</td><td class="${c.change>=0?'green':'red'}">${c.change>=0?'+':''}${c.change.toFixed(1)}%</td></tr>`).join('')}</table></div>
                        <div class="card"><h3>信号</h3><div class="signal-${data.btc_signal.toLowerCase()}"><span>${data.btc_signal}</span><p style="color:#888;margin-top:10px">${data.btc_reasons}</p></div></div>
                    </div>`;
                const chartData = await fetch("/api/chart/btc").then(r=>r.json());
                new Chart(document.getElementById("chart"),{type:"line",data:{labels:chartData.labels,datasets:[{label:"Price",data:chartData.prices,borderColor:"#f0b90b",fill:true,tension:0.4}]},options:{responsive:true,plugins:{legend:{display:false}}}});
            }
            else if (page === "analysis") {
                const resp = await fetch("/api/analyze/BTCUSDT");
                const data = await resp.json();
                content.innerHTML = `
                    <div class="card"><h3>BTC/USDT 完整分析</h3>
                    <div class="grid">
                        <div><h4>价格</h4><div class="price">$${data.ticker.price.toLocaleString()}</div><div class="${data.ticker.change_24h>=0?'green':'red'}">${data.ticker.change_24h.toFixed(2)}%</div></div>
                        <div><h4>RSI</h4><div class="value">${data.analysis.rsi}</div></div>
                        <div><h4>趋势</h4><div class="value">${data.analysis.trend}</div></div>
                        <div><h4>信号</h4><div class="value">${data.analysis.signal}</div></div>
                    </div>
                    <div style="margin-top:20px"><h4>MACD</h4><pre>${JSON.stringify(data.analysis.macd,null,2)}</pre></div>
                    </div>`;
            }
            else if (page === "whales") {
                const resp = await fetch("/api/whales/BTC");
                const data = await resp.json();
                content.innerHTML = `
                    <div class="card"><h3>🐋 BTC 巨鲸分析</h3>
                    <div class="grid">
                        <div><h4>OI</h4><div class="value">$${(data.oi.open_interest/1e9).toFixed(1)}B</div></div>
                        <div><h4>多空比</h4><div class="value">${data.oi.long_ratio}% / ${data.oi.short_ratio}%</div></div>
                        <div><h4>资金费率</h4><div class="value">${data.oi.funding_rate}%</div></div>
                        <div><h4>情绪</h4><div class="value">${data.oi.sentiment}</div></div>
                    </div>
                    <div class="whale-alert"><h4>📉 清算区域</h4><p>支撑: ${data.liquidation.major_support?.join(', ') || 'N/A'}</p><p>阻力: ${data.liquidation.major_resistance?.join(', ') || 'N/A'}</p></div>
                    </div>`;
            }
            else if (page === "alpha") {
                const resp = await fetch("/api/alpha");
                const data = await resp.json();
                content.innerHTML = `<div class="card"><h3>🎯 Alpha 探测雷达</h3><pre style="white-space:pre-wrap;font-size:14px">${data.report}</pre><button class="btn" onclick="loadPage('alpha')">刷新</button></div>`;
            }
            else if (page === "multi") {
                const resp = await fetch("/api/multichain");
                const data = await resp.json();
                content.innerHTML = `<div class="card"><h3>🔥 多链热点</h3><pre>${data.report}</pre></div>`;
            }
            else if (page === "safety") {
                content.innerHTML = `
                    <div class="card"><h3>🔐 代币安全审计</h3>
                    <input type="text" id="tokenAddr" placeholder="输入代币地址" style="width:300px">
                    <button class="btn" onclick="checkToken()">检测</button>
                    <div id="result" style="margin-top:20px"></div>
                    </div>`;
            }
            else if (page === "copy") {
                const resp = await fetch("/api/signals/solana");
                const data = await resp.json();
                content.innerHTML = `
                    <div class="card"><h3>👥 Smart Money 信号</h3>
                    ${data.signals.map(s=>`<div class="whale-alert"><b>${s.source}</b>: ${s.token} ${s.action} $${s.amount_usd?.toLocaleString()}</div>`).join('')}
                    <button class="btn" onclick="loadPage('copy')">刷新</button>
                    </div>`;
            }
            else if (page === "joint") {
                content.innerHTML = `
                    <div class="card"><h3>💑 共同账户</h3>
                    <input type="text" id="accountName" placeholder="账户名称" value="买房基金">
                    <input type="number" id="goalAmount" placeholder="目标金额" value="5">
                    <select id="tokenType"><option>USDT</option><option>BTC</option><option>ETH</option></select>
                    <button class="btn" onclick="createJoint()">创建</button>
                    <div id="jointResult"></div>
                    </div>`;
            }
            else if (page === "post") {
                content.innerHTML = `
                    <div class="card"><h3>📝 AI Post 生成器</h3>
                    <input type="text" id="postSymbol" placeholder="币种" value="BTC">
                    <button class="btn" onclick="generatePost()">生成</button>
                    <pre id="postResult" style="background:#000;padding:20px;margin-top:20px;border-radius:10px;white-space:pre-wrap"></pre>
                    <button class="btn" onclick="copyPost()">复制</button>
                    </div>`;
            }
        }
        async function checkToken() {
            const addr = document.getElementById("tokenAddr").value;
            const resp = await fetch("/api/honeypot/" + (addr || "test"));
            const data = await resp.json();
            document.getElementById("result").innerHTML = `<div class="joint-account">${data.report}</div>`;
        }
        async function createJoint() {
            const name = document.getElementById("accountName").value;
            const goal = document.getElementById("goalAmount").value;
            const token = document.getElementById("tokenType").value;
            const resp = await fetch("/api/joint?goal="+goal+"&token="+token+"&name="+name);
            const data = await resp.json();
            document.getElementById("jointResult").innerHTML = data.progress;
        }
        async function generatePost() {
            const symbol = document.getElementById("postSymbol").value;
            const resp = await fetch("/api/post/" + symbol);
            const data = await resp.json();
            document.getElementById("postResult").textContent = data.post;
        }
        function copyPost() {
            navigator.clipboard.writeText(document.getElementById("postResult").textContent);
            alert("已复制!");
        }
        loadPage("dashboard");
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

# API Endpoints
@app.route('/api/dashboard')
def dashboard():
    btc = get_24h_ticker("BTCUSDT")
    eth = get_24h_ticker("ETHUSDT")
    top = get_top_coins(5)
    oi = get_open_interest("BTC")
    sentiment = get_market_sentiment("BTC")
    klines = get_klines("BTCUSDT", "1h", 50)
    prices = [k["close"] for k in klines]
    analysis = analyze_market(prices)
    return jsonify({
        "btc": {"price": btc["price"], "change": btc["change_24h"]},
        "eth": {"price": eth["price"], "change": eth["change_24h"]},
        "sentiment": sentiment,
        "btc_oi": oi.get("open_interest", 0),
        "btc_oi_change": oi.get("change_24h", 0),
        "top": [{"symbol": t["symbol"], "price": t["price"], "change": t["change_24h"]} for t in top],
        "btc_signal": analysis.get("signal", "观望"),
        "btc_reasons": analysis.get("reasons", "")
    })

@app.route('/api/chart/<symbol>')
def chart(symbol):
    klines = get_klines(f"{symbol}USDT", "1h", 50)
    return jsonify({
        "labels": [f"{i}" for i in range(50)],
        "prices": [k["close"] for k in klines]
    })

@app.route('/api/analyze/<symbol>')
def analyze(symbol):
    ticker = get_24h_ticker(f"{symbol}USDT")
    klines = get_klines(f"{symbol}USDT", "1h", 100)
    prices = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    return jsonify({
        "ticker": ticker,
        "analysis": analyze_market(prices, volumes)
    })

@app.route('/api/whales/<symbol>')
def whales(symbol):
    oi = get_open_interest(symbol)
    liq = get_liquidation_clusters(symbol)
    return jsonify({"oi": oi, "liquidation": liq})

@app.route('/api/multichain')
def multichain():
    return jsonify({"report": get_multi_chain_report()})

@app.route('/api/honeypot/<token>')
def honeypot(token):
    return jsonify({"report": check_token_safety(token)})

@app.route('/api/signals/<chain>')
def signals(chain):
    return jsonify({"signals": get_smart_money_signals(chain)})

@app.route('/api/joint')
def joint():
    from utils.joint_account import create_joint_account
    name = request.args.get("name", "购房基金")
    goal = float(request.args.get("goal", 5))
    token = request.args.get("token", "USDT")
    acc = create_joint_account(name, goal, token)
    return jsonify({"progress": acc.get_progress()})

@app.route('/api/post/<symbol>')
def post(symbol):
    from utils.post_generator import generate_post_basic
    return jsonify({"post": generate_post_basic(symbol)})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    print(f"🌐 Starting Complete Web Dashboard on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

@app.route('/api/alpha')
def alpha():
    from utils.alpha_radar import get_alpha_signals
    return jsonify({"report": get_alpha_signals()})
