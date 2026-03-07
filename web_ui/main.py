"""
Binance AI Assistant Web Dashboard
Stable + guardrail-enhanced edition.
"""
import os
import sys
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template_string, jsonify, request
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from indicators.indicators import analyze_market
from utils.binance_api import get_24h_ticker, get_klines, get_top_coins
from utils.whale_tracker import get_open_interest, get_market_sentiment, get_liquidation_clusters
from utils.multi_chain_scanner import get_multi_chain_report
from utils.honeypot_detector import check_token_safety
from utils.social_trading import get_smart_money_signals
from utils.joint_account import create_joint_account
from utils.alpha_radar import get_alpha_signals
from post_generator.main import generate_post_basic
from utils.user_guardrails import (
    calculate_position_size,
    evaluate_guardrail,
    get_user_guardrail_config,
    update_user_guardrail_config,
    add_journal_entry,
    list_journal,
    get_daily_review,
)
from utils.persistence import (
    init_db,
    create_user,
    get_user,
    insert_position,
    list_positions,
    update_position_risk,
    close_position,
)
from utils.trading_advisor import build_entry_suggestion

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "change-this-in-production")
serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])
init_db()


HTML = """
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Binance Market Pulse AI</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #090f1f;
      --bg-soft: #0f1830;
      --panel: rgba(16, 27, 51, 0.88);
      --line: rgba(255, 255, 255, 0.12);
      --text: #e8edf8;
      --muted: #9db0d2;
      --up: #11c58a;
      --down: #ff5c7a;
      --accent: #f0b90b;
      --accent-2: #56b5ff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--text);
      font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at 10% 10%, rgba(86,181,255,0.20), transparent 30%),
        radial-gradient(circle at 90% 0%, rgba(240,185,11,0.12), transparent 35%),
        linear-gradient(135deg, var(--bg) 0%, #111f42 100%);
      min-height: 100vh;
    }
    .header {
      position: sticky;
      top: 0;
      z-index: 9;
      backdrop-filter: blur(8px);
      background: rgba(6, 11, 24, 0.8);
      border-bottom: 1px solid var(--line);
      padding: 14px 20px;
      display: flex;
      gap: 14px;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
    }
    .brand { font-size: 20px; font-weight: 700; color: var(--accent); }
    .nav { display: flex; gap: 8px; flex-wrap: wrap; }
    .auth {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
      justify-content: flex-end;
    }
    .auth input {
      max-width: 140px;
      padding: 8px;
    }
    .auth .user {
      font-size: 12px;
      color: var(--muted);
      margin-right: 4px;
    }
    .nav button {
      border: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.04);
      color: var(--muted);
      border-radius: 999px;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 13px;
    }
    .nav button.active,
    .nav button:hover { background: var(--accent); color: #1d1602; border-color: transparent; }
    .container { max-width: 1280px; margin: 0 auto; padding: 22px; }
    .grid { display: grid; gap: 14px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
    .card {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 16px;
      padding: 16px;
      box-shadow: 0 10px 30px rgba(2, 6, 16, 0.4);
    }
    h2, h3, h4 { margin: 0 0 10px; }
    .muted { color: var(--muted); font-size: 13px; }
    .price { font-size: 34px; font-weight: 700; }
    .value { font-size: 22px; font-weight: 700; }
    .up { color: var(--up); }
    .down { color: var(--down); }
    .row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    input, select, textarea {
      width: 100%;
      max-width: 300px;
      background: rgba(255, 255, 255, 0.04);
      color: var(--text);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px;
    }
    textarea { min-height: 100px; max-width: 100%; }
    button.btn {
      border: none;
      background: linear-gradient(135deg, var(--accent), #ffd565);
      color: #201600;
      border-radius: 10px;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
    }
    button.btn:hover { filter: brightness(0.95); }
    pre {
      white-space: pre-wrap;
      margin: 0;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 12px;
      color: #d8e4ff;
    }
    table { width: 100%; border-collapse: collapse; }
    th, td { border-bottom: 1px solid var(--line); padding: 10px 6px; text-align: left; font-size: 14px; }
    .pill { display: inline-block; border-radius: 999px; padding: 4px 10px; font-size: 12px; border: 1px solid var(--line); }
    .ok { background: rgba(17, 197, 138, 0.15); color: var(--up); }
    .warn { background: rgba(255, 92, 122, 0.15); color: var(--down); }
    .err { color: #ff9fb2; margin-top: 10px; }

    @media (max-width: 800px) {
      .container { padding: 14px; }
      .price { font-size: 28px; }
    }
  </style>
</head>
<body>
  <header class="header">
    <div class="brand">Binance Market Pulse AI</div>
    <nav class="nav" id="nav"></nav>
    <div class="auth" id="authBox">
      <span class="user" id="authUser">未登录</span>
      <input id="authName" placeholder="用户名" />
      <input id="authPass" type="password" placeholder="密码" />
      <button class="btn" onclick="registerUser()">注册</button>
      <button class="btn" onclick="loginUser()">登录</button>
      <button class="btn" onclick="logoutUser()">退出</button>
    </div>
  </header>
  <main class="container" id="content">加载中...</main>

  <script>
    let authToken = localStorage.getItem("auth_token") || "";
    let currentUser = localStorage.getItem("auth_user") || "";

    const pages = [
      ["dashboard", "仪表盘"],
      ["analysis", "分析"],
      ["whales", "巨鲸"],
      ["alpha", "Alpha"],
      ["multi", "多链"],
      ["safety", "安全"],
      ["copy", "跟单"],
      ["joint", "共同账户"],
      ["post", "发推"],
      ["planner", "开仓建议"],
      ["positions", "仓位管理"],
      ["risk", "风控"],
      ["journal", "日志"],
      ["review", "复盘"]
    ];

    const nav = document.getElementById("nav");
    for (const [key, label] of pages) {
      const b = document.createElement("button");
      b.textContent = label;
      b.onclick = () => showPage(key);
      b.dataset.page = key;
      nav.appendChild(b);
    }

    updateAuthUI();

    function setActive(page) {
      document.querySelectorAll(".nav button").forEach((b) => {
        b.classList.toggle("active", b.dataset.page === page);
      });
    }

    async function apiGet(url) {
      const headers = authToken ? {"Authorization": `Bearer ${authToken}`} : {};
      const r = await fetch(url, {headers});
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "请求失败");
      return data;
    }

    async function apiPost(url, body) {
      const headers = {"Content-Type": "application/json"};
      if (authToken) headers["Authorization"] = `Bearer ${authToken}`;
      const r = await fetch(url, {
        method: "POST",
        headers,
        body: JSON.stringify(body || {})
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error || "请求失败");
      return data;
    }

    function updateAuthUI() {
      const userEl = document.getElementById("authUser");
      userEl.textContent = currentUser ? `已登录: ${currentUser}` : "未登录";
    }

    async function registerUser() {
      const username = document.getElementById("authName").value.trim();
      const password = document.getElementById("authPass").value.trim();
      try {
        await apiPost("/api/auth/register", {username, password});
        alert("注册成功，请登录");
      } catch (e) {
        alert(e.message);
      }
    }

    async function loginUser() {
      const username = document.getElementById("authName").value.trim();
      const password = document.getElementById("authPass").value.trim();
      try {
        const data = await apiPost("/api/auth/login", {username, password});
        authToken = data.token;
        currentUser = data.username;
        localStorage.setItem("auth_token", authToken);
        localStorage.setItem("auth_user", currentUser);
        updateAuthUI();
        alert("登录成功");
      } catch (e) {
        alert(e.message);
      }
    }

    function logoutUser() {
      authToken = "";
      currentUser = "";
      localStorage.removeItem("auth_token");
      localStorage.removeItem("auth_user");
      updateAuthUI();
      alert("已退出");
    }

    function formatChange(v) {
      const cls = v >= 0 ? "up" : "down";
      const sign = v >= 0 ? "+" : "";
      return `<span class="${cls}">${sign}${v.toFixed(2)}%</span>`;
    }

    async function showPage(page) {
      setActive(page);
      const content = document.getElementById("content");
      content.innerHTML = "<div class='card'>加载中...</div>";

      try {
        if (page === "dashboard") {
          const data = await apiGet("/api/dashboard");
          content.innerHTML = `
            <div class="grid">
              <section class="card"><h3>BTC</h3><div class="price">$${data.btc.price.toLocaleString()}</div>${formatChange(data.btc.change)}</section>
              <section class="card"><h3>ETH</h3><div class="price">$${data.eth.price.toLocaleString()}</div>${formatChange(data.eth.change)}</section>
              <section class="card"><h3>市场情绪</h3><div class="value">${data.sentiment}</div><p class="muted">基于资金费率与多空结构</p></section>
              <section class="card"><h3>BTC OI</h3><div class="value">$${(data.btc_oi/1e9).toFixed(2)}B</div>${formatChange(data.btc_oi_change)}</section>
            </div>
            <section class="card" style="margin-top:14px"><h3>BTC/USDT 1h</h3><canvas id="chart" height="92"></canvas></section>
            <div class="grid" style="margin-top:14px">
              <section class="card">
                <h3>热门代币</h3>
                <table><tbody>
                ${data.top.map((c, i) => `<tr><td>${i+1}</td><td>${c.symbol}</td><td>$${c.price.toFixed(4)}</td><td>${formatChange(c.change)}</td></tr>`).join("")}
                </tbody></table>
              </section>
              <section class="card">
                <h3>技术信号</h3>
                <div class="pill ${data.btc_signal === "买入" ? "ok" : data.btc_signal === "卖出" ? "warn" : ""}">${data.btc_signal}</div>
                <p class="muted" style="margin-top:10px">${data.btc_reasons}</p>
              </section>
            </div>`;

          const chartData = await apiGet("/api/chart/BTC");
          const ctx = document.getElementById("chart");
          new Chart(ctx, {
            type: "line",
            data: {
              labels: chartData.labels,
              datasets: [{
                data: chartData.prices,
                borderColor: "#f0b90b",
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.28,
                fill: true,
                backgroundColor: "rgba(240,185,11,0.15)"
              }]
            },
            options: { plugins: { legend: { display: false } } }
          });
        }

        if (page === "analysis") {
          const symbol = "BTCUSDT";
          const data = await apiGet(`/api/analyze/${symbol}`);
          content.innerHTML = `
            <section class="card">
              <h2>${symbol} 完整分析</h2>
              <div class="grid">
                <div><p class="muted">价格</p><div class="price">$${data.ticker.price.toLocaleString()}</div>${formatChange(data.ticker.change_24h)}</div>
                <div><p class="muted">RSI</p><div class="value">${data.analysis.rsi}</div></div>
                <div><p class="muted">趋势</p><div class="value">${data.analysis.trend}</div></div>
                <div><p class="muted">信号</p><div class="value">${data.analysis.signal}</div></div>
              </div>
              <h4 style="margin-top:14px">MACD</h4>
              <pre>${JSON.stringify(data.analysis.macd, null, 2)}</pre>
            </section>`;
        }

        if (page === "whales") {
          const data = await apiGet("/api/whales/BTC");
          content.innerHTML = `
            <section class="card">
              <h2>BTC 巨鲸行为</h2>
              <div class="grid">
                <div><p class="muted">Open Interest</p><div class="value">$${(data.oi.open_interest/1e9).toFixed(2)}B</div></div>
                <div><p class="muted">多空比</p><div class="value">${data.oi.long_ratio}% / ${data.oi.short_ratio}%</div></div>
                <div><p class="muted">资金费率</p><div class="value">${data.oi.funding_rate}%</div></div>
                <div><p class="muted">情绪</p><div class="value">${data.oi.sentiment}</div></div>
              </div>
              <div style="margin-top:12px" class="card">
                <h4>清算区域</h4>
                <p class="muted">支撑: ${(data.liquidation.major_support || []).join(", ") || "N/A"}</p>
                <p class="muted">阻力: ${(data.liquidation.major_resistance || []).join(", ") || "N/A"}</p>
              </div>
            </section>`;
        }

        if (page === "alpha") {
          const data = await apiGet("/api/alpha");
          content.innerHTML = `<section class="card"><h2>Alpha Radar</h2><pre>${data.report}</pre></section>`;
        }

        if (page === "multi") {
          const data = await apiGet("/api/multichain");
          content.innerHTML = `<section class="card"><h2>多链热点</h2><pre>${data.report}</pre></section>`;
        }

        if (page === "safety") {
          content.innerHTML = `
            <section class="card">
              <h2>代币安全审计</h2>
              <p class="muted">输入地址后进行 Honeypot/安全检查</p>
              <div class="row">
                <input id="tokenAddr" placeholder="输入代币地址" />
                <button class="btn" onclick="checkToken()">检测</button>
              </div>
              <div id="tokenResult" style="margin-top:10px"></div>
            </section>`;
        }

        if (page === "copy") {
          const data = await apiGet("/api/signals/solana");
          content.innerHTML = `
            <section class="card">
              <h2>Smart Money 信号</h2>
              ${data.signals.map(s => `<div class="card" style="margin-top:8px"><b>${s.source}</b> ${s.action} ${s.token} $${(s.amount || 0).toLocaleString()}<br/><span class="muted">置信度 ${s.confidence || 0}% · ${s.time}</span></div>`).join("")}
            </section>`;
        }

        if (page === "joint") {
          content.innerHTML = `
            <section class="card">
              <h2>共同账户</h2>
              <div class="row">
                <input id="accountName" value="买房基金" placeholder="账户名称" />
                <input id="goalAmount" type="number" value="5" placeholder="目标金额" />
                <select id="tokenType"><option>USDT</option><option>BTC</option><option>ETH</option></select>
                <button class="btn" onclick="createJoint()">创建</button>
              </div>
              <pre id="jointResult" style="margin-top:10px"></pre>
            </section>`;
        }

        if (page === "post") {
          content.innerHTML = `
            <section class="card">
              <h2>AI Post 生成器</h2>
              <div class="row">
                <input id="postSymbol" value="BTC" placeholder="币种" />
                <button class="btn" onclick="generatePost()">生成</button>
                <button class="btn" onclick="copyPost()">复制</button>
              </div>
              <pre id="postResult" style="margin-top:10px"></pre>
            </section>`;
        }

        if (page === "planner") {
          content.innerHTML = `
            <section class="card">
              <h2>仅开仓建议</h2>
              <p class="muted">给出现货/合约/链上的开仓允许与风控计划（TP/SL）</p>
              <div class="row">
                <input id="planSymbol" value="BTCUSDT" placeholder="交易对，如 BTCUSDT" />
                <select id="planMarket">
                  <option value="spot">spot</option>
                  <option value="futures">futures</option>
                  <option value="onchain">onchain</option>
                </select>
                <select id="planSide">
                  <option value="LONG">LONG</option>
                  <option value="SHORT">SHORT</option>
                </select>
                <button class="btn" onclick="fetchEntrySuggestion()">生成建议</button>
              </div>
              <pre id="planResult" style="margin-top:10px"></pre>
            </section>`;
        }

        if (page === "positions") {
          content.innerHTML = `
            <div class="grid">
              <section class="card">
                <h2>创建仓位</h2>
                <div class="row"><select id="posMarket"><option value="spot">spot</option><option value="futures">futures</option><option value="onchain">onchain</option></select></div>
                <div class="row"><select id="posSide"><option value="LONG">LONG</option><option value="SHORT">SHORT</option></select></div>
                <div class="row"><input id="posSymbol" value="BTCUSDT" placeholder="交易对" /></div>
                <div class="row"><input id="posEntry" type="number" value="65000" placeholder="入场价" /></div>
                <div class="row"><input id="posQty" type="number" step="0.0001" value="0.01" placeholder="数量" /></div>
                <div class="row"><input id="posLev" type="number" step="0.1" value="1" placeholder="杠杆" /></div>
                <div class="row"><input id="posSL" type="number" step="0.0001" placeholder="止损价" /></div>
                <div class="row"><input id="posTP1" type="number" step="0.0001" placeholder="止盈1" /></div>
                <div class="row"><input id="posTP2" type="number" step="0.0001" placeholder="止盈2" /></div>
                <div class="row"><input id="posTP3" type="number" step="0.0001" placeholder="止盈3" /></div>
                <button class="btn" onclick="createPosition()">创建仓位</button>
              </section>
              <section class="card">
                <h2>我的仓位</h2>
                <div class="row">
                  <select id="posStatus"><option value="OPEN">OPEN</option><option value="CLOSED">CLOSED</option></select>
                  <select id="posFilterMarket"><option value="">all</option><option value="spot">spot</option><option value="futures">futures</option><option value="onchain">onchain</option></select>
                  <button class="btn" onclick="loadPositions()">刷新</button>
                </div>
                <div id="positionsList" style="margin-top:10px"></div>
              </section>
            </div>`;
          await loadPositions();
        }

        if (page === "risk") {
          content.innerHTML = `
            <div class="grid">
              <section class="card">
                <h2>仓位风险计算器</h2>
                <p class="muted">按账户规模、风险比例、止损距离自动算仓位</p>
                <div class="row"><input id="accountSize" type="number" value="10000" placeholder="账户资金" /></div>
                <div class="row"><input id="riskPct" type="number" step="0.1" value="1" placeholder="单笔风险%" /></div>
                <div class="row"><input id="entryPrice" type="number" value="65000" placeholder="入场价" /></div>
                <div class="row"><input id="stopPrice" type="number" value="63500" placeholder="止损价" /></div>
                <div class="row"><input id="leverage" type="number" step="0.1" value="3" placeholder="杠杆" /></div>
                <button class="btn" onclick="calcRisk()">计算</button>
                <pre id="riskResult" style="margin-top:10px"></pre>
              </section>

              <section class="card">
                <h2>交易纪律守护器</h2>
                <p class="muted">防止高频冲动交易与连亏上头</p>
                <div class="row"><input id="maxTradesPerDay" type="number" value="8" placeholder="日内最大交易次数" /></div>
                <div class="row"><input id="cooldownLosses" type="number" value="3" placeholder="连续亏损触发数" /></div>
                <div class="row"><input id="cooldownMinutes" type="number" value="45" placeholder="冷静期(分钟)" /></div>
                <div class="row"><select id="guardOutcome"><option value="win">盈利</option><option value="loss">亏损</option><option value="open">未平仓</option></select></div>
                <div class="row"><button class="btn" onclick="saveGuardConfig()">保存规则</button><button class="btn" onclick="evalGuard()">更新并评估</button></div>
                <pre id="guardResult" style="margin-top:10px"></pre>
              </section>
            </div>`;
          await loadGuardConfig();
        }

        if (page === "journal") {
          content.innerHTML = `
            <section class="card">
              <h2>交易日志</h2>
              <p class="muted">降低复盘摩擦，记录主观决策和情绪</p>
              <div class="row"><input id="jSymbol" value="BTCUSDT" placeholder="交易对" /></div>
              <div class="row"><select id="jSide"><option>BUY</option><option>SELL</option></select><select id="jMarket"><option value="spot">spot</option><option value="futures">futures</option><option value="onchain">onchain</option></select><select id="jEmotion"><option>neutral</option><option>fear</option><option>fomo</option><option>calm</option></select></div>
              <div class="row"><input id="jPnl" type="number" step="0.01" placeholder="本单盈亏(USDT)" /><select id="jResult"><option value="open">open</option><option value="win">win</option><option value="loss">loss</option></select></div>
              <div class="row"><input id="jTags" placeholder="标签，逗号分隔 (breakout,news)" /></div>
              <textarea id="jThesis" placeholder="为什么开这笔单？"></textarea>
              <div class="row"><button class="btn" onclick="addJournal()">保存日志</button><button class="btn" onclick="loadJournal()">刷新列表</button></div>
              <div id="journalList" style="margin-top:10px"></div>
            </section>`;
          await loadJournal();
        }

        if (page === "review") {
          content.innerHTML = `
            <section class="card">
              <h2>每日交易复盘</h2>
              <p class="muted">按现货/合约/链上维度统计胜率与净盈亏</p>
              <div class="row">
                <input id="reviewDate" type="date" />
                <button class="btn" onclick="loadDailyReview()">生成复盘</button>
              </div>
              <pre id="reviewResult" style="margin-top:10px"></pre>
            </section>`;
          const now = new Date().toISOString().slice(0, 10);
          document.getElementById("reviewDate").value = now;
          await loadDailyReview();
        }
      } catch (e) {
        content.innerHTML = `<section class="card"><h3>加载失败</h3><div class="err">${e.message}</div></section>`;
      }
    }

    async function checkToken() {
      const addr = document.getElementById("tokenAddr").value || "test";
      const data = await apiGet("/api/honeypot/" + encodeURIComponent(addr));
      document.getElementById("tokenResult").innerHTML = `<pre>${data.report}</pre>`;
    }

    async function createJoint() {
      const name = document.getElementById("accountName").value;
      const goal = document.getElementById("goalAmount").value;
      const token = document.getElementById("tokenType").value;
      const data = await apiGet(`/api/joint?name=${encodeURIComponent(name)}&goal=${goal}&token=${token}`);
      document.getElementById("jointResult").textContent = data.progress;
    }

    async function generatePost() {
      const symbol = document.getElementById("postSymbol").value || "BTC";
      const data = await apiGet("/api/post/" + encodeURIComponent(symbol));
      document.getElementById("postResult").textContent = data.post;
    }

    function copyPost() {
      navigator.clipboard.writeText(document.getElementById("postResult").textContent || "");
      alert("已复制");
    }

    async function calcRisk() {
      const payload = {
        account_size: Number(document.getElementById("accountSize").value),
        risk_pct: Number(document.getElementById("riskPct").value),
        entry_price: Number(document.getElementById("entryPrice").value),
        stop_price: Number(document.getElementById("stopPrice").value),
        leverage: Number(document.getElementById("leverage").value)
      };
      const data = await apiPost("/api/risk/position-size", payload);
      document.getElementById("riskResult").textContent = JSON.stringify(data, null, 2);
    }

    function ensureAuth() {
      if (!authToken) {
        throw new Error("请先登录后使用该功能");
      }
    }

    async function loadGuardConfig() {
      ensureAuth();
      const data = await apiGet("/api/guardrails/config");
      document.getElementById("maxTradesPerDay").value = data.config.max_trades_per_day;
      document.getElementById("cooldownLosses").value = data.config.cooldown_losses;
      document.getElementById("cooldownMinutes").value = data.config.cooldown_minutes;
    }

    async function saveGuardConfig() {
      ensureAuth();
      const payload = {
        max_trades_per_day: Number(document.getElementById("maxTradesPerDay").value),
        cooldown_losses: Number(document.getElementById("cooldownLosses").value),
        cooldown_minutes: Number(document.getElementById("cooldownMinutes").value)
      };
      const data = await apiPost("/api/guardrails/config", payload);
      document.getElementById("guardResult").textContent = JSON.stringify({config_saved: data.config}, null, 2);
    }

    async function evalGuard() {
      ensureAuth();
      const payload = { outcome: document.getElementById("guardOutcome").value };
      const data = await apiPost("/api/guardrails/evaluate", payload);
      document.getElementById("guardResult").textContent = JSON.stringify(data, null, 2);
    }

    async function fetchEntrySuggestion() {
      ensureAuth();
      const payload = {
        symbol: document.getElementById("planSymbol").value,
        market_type: document.getElementById("planMarket").value,
        side: document.getElementById("planSide").value
      };
      const data = await apiPost("/api/entry-suggestion", payload);
      document.getElementById("planResult").textContent = JSON.stringify(data, null, 2);
    }

    async function createPosition() {
      ensureAuth();
      const payload = {
        market_type: document.getElementById("posMarket").value,
        side: document.getElementById("posSide").value,
        symbol: document.getElementById("posSymbol").value,
        entry_price: Number(document.getElementById("posEntry").value),
        quantity: Number(document.getElementById("posQty").value),
        leverage: Number(document.getElementById("posLev").value),
        stop_loss: Number(document.getElementById("posSL").value || 0) || null,
        take_profit_1: Number(document.getElementById("posTP1").value || 0) || null,
        take_profit_2: Number(document.getElementById("posTP2").value || 0) || null,
        take_profit_3: Number(document.getElementById("posTP3").value || 0) || null
      };
      await apiPost("/api/positions", payload);
      await loadPositions();
    }

    async function updatePositionRisk(positionId) {
      ensureAuth();
      const sl = prompt("新的止损价 (留空则不改)");
      const tp1 = prompt("新的止盈1价 (留空则不改)");
      const tp2 = prompt("新的止盈2价 (留空则不改)");
      const tp3 = prompt("新的止盈3价 (留空则不改)");
      const payload = {
        stop_loss: sl ? Number(sl) : null,
        take_profit_1: tp1 ? Number(tp1) : null,
        take_profit_2: tp2 ? Number(tp2) : null,
        take_profit_3: tp3 ? Number(tp3) : null
      };
      await apiPost(`/api/positions/${positionId}/risk`, payload);
      await loadPositions();
    }

    async function closeOnePosition(positionId) {
      ensureAuth();
      const price = prompt("平仓价格");
      if (!price) return;
      const reason = prompt("平仓原因", "manual") || "manual";
      await apiPost(`/api/positions/${positionId}/close`, { close_price: Number(price), close_reason: reason });
      await loadPositions();
    }

    async function loadPositions() {
      ensureAuth();
      const statusEl = document.getElementById("posStatus");
      const marketEl = document.getElementById("posFilterMarket");
      const status = statusEl ? statusEl.value : "OPEN";
      const market = marketEl ? marketEl.value : "";
      const data = await apiGet(`/api/positions?status=${encodeURIComponent(status)}&market_type=${encodeURIComponent(market)}`);
      const html = (data.positions || []).map((p) => `
        <div class="card" style="margin-top:8px">
          <b>#${p.id}</b> ${p.market_type} ${p.symbol} ${p.side} ${p.status}<br/>
          入场: ${Number(p.entry_price).toFixed(4)} | 数量: ${Number(p.quantity).toFixed(6)} | 杠杆: ${Number(p.leverage).toFixed(2)}x<br/>
          SL: ${p.stop_loss ?? "-"} | TP1: ${p.take_profit_1 ?? "-"} | TP2: ${p.take_profit_2 ?? "-"} | TP3: ${p.take_profit_3 ?? "-"}<br/>
          ${p.pnl != null ? `PnL: ${Number(p.pnl).toFixed(2)}<br/>` : ""}
          ${status === "OPEN" ? `<button class="btn" onclick="updatePositionRisk(${p.id})">改TP/SL</button> <button class="btn" onclick="closeOnePosition(${p.id})">平仓</button>` : ""}
        </div>
      `).join("") || '<p class="muted">暂无记录</p>';
      document.getElementById("positionsList").innerHTML = html;
    }

    async function loadDailyReview() {
      ensureAuth();
      const date = document.getElementById("reviewDate").value;
      const data = await apiGet(`/api/review/daily?date=${encodeURIComponent(date)}`);
      document.getElementById("reviewResult").textContent = JSON.stringify(data, null, 2);
    }

    async function addJournal() {
      ensureAuth();
      const payload = {
        symbol: document.getElementById("jSymbol").value,
        side: document.getElementById("jSide").value,
        market_type: document.getElementById("jMarket").value,
        emotion: document.getElementById("jEmotion").value,
        result: document.getElementById("jResult").value,
        pnl: Number(document.getElementById("jPnl").value || 0),
        thesis: document.getElementById("jThesis").value,
        tags: (document.getElementById("jTags").value || "").split(",").map(s => s.trim()).filter(Boolean)
      };
      await apiPost("/api/journal", payload);
      document.getElementById("jThesis").value = "";
      await loadJournal();
    }

    async function loadJournal() {
      ensureAuth();
      const data = await apiGet("/api/journal?limit=20");
      const html = data.entries.map((e) =>
        `<div class="card" style="margin-top:8px"><b>${e.symbol}</b> ${e.side} <span class="pill">${e.market_type}</span> <span class="pill">${e.emotion}</span> <span class="muted">${e.time}</span><br/>结果: ${e.result} | PnL: ${Number(e.pnl || 0).toFixed(2)}<br/><span>${e.thesis || "-"}</span><br/><span class="muted">${(e.tags || []).join(", ")}</span></div>`
      ).join("") || '<p class="muted">暂无日志</p>';
      document.getElementById("journalList").innerHTML = html;
    }

    showPage("dashboard");
  </script>
</body>
</html>
"""


def api_ok(payload: dict, status: int = 200):
    return jsonify(payload), status


def create_token(username: str) -> str:
    return serializer.dumps({"username": username})


def resolve_user_from_request(max_age_seconds: int = 7 * 24 * 3600):
    auth_header = request.headers.get("Authorization", "")
    token = request.headers.get("X-Auth-Token")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
        return data.get("username")
    except (BadSignature, SignatureExpired):
        return None


def auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        username = resolve_user_from_request()
        if not username:
            return api_ok({"error": "未登录或登录已过期"}, 401)
        request.current_user = username
        return fn(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    try:
        payload = request.get_json(force=True) or {}
        username = str(payload.get("username", "")).strip().lower()
        password = str(payload.get("password", "")).strip()

        if len(username) < 3:
            return api_ok({"error": "用户名至少3位"}, 400)
        if len(password) < 6:
            return api_ok({"error": "密码至少6位"}, 400)

        ok = create_user(
            username=username,
            password_hash=generate_password_hash(password),
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        if not ok:
            return api_ok({"error": "用户名已存在"}, 409)
        return api_ok({"ok": True}, 201)
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    try:
        payload = request.get_json(force=True) or {}
        username = str(payload.get("username", "")).strip().lower()
        password = str(payload.get("password", "")).strip()

        user = get_user(username)
        if not user or not check_password_hash(user["password_hash"], password):
            return api_ok({"error": "用户名或密码错误"}, 401)

        token = create_token(username)
        return api_ok({"token": token, "username": username})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    username = resolve_user_from_request()
    if not username:
        return api_ok({"error": "未登录"}, 401)
    return api_ok({"username": username})


@app.route("/api/dashboard")
def dashboard():
    try:
        btc = get_24h_ticker("BTCUSDT")
        eth = get_24h_ticker("ETHUSDT")
        top = get_top_coins(6)
        oi = get_open_interest("BTC")
        sentiment = get_market_sentiment("BTC")
        klines = get_klines("BTCUSDT", "1h", 50)
        prices = [k["close"] for k in klines]
        analysis = analyze_market(prices)

        return api_ok(
            {
                "btc": {"price": btc["price"], "change": btc["change_24h"]},
                "eth": {"price": eth["price"], "change": eth["change_24h"]},
                "sentiment": sentiment,
                "btc_oi": oi.get("open_interest", 0),
                "btc_oi_change": oi.get("change_24h", 0),
                "top": [
                    {"symbol": t["symbol"], "price": t["price"], "change": t["change_24h"]}
                    for t in top
                ],
                "btc_signal": analysis.get("signal", "观望"),
                "btc_reasons": analysis.get("reasons", ""),
            }
        )
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/chart/<symbol>")
def chart(symbol):
    try:
        pair = f"{symbol.upper()}USDT" if not symbol.upper().endswith("USDT") else symbol.upper()
        klines = get_klines(pair, "1h", 50)
        return api_ok({"labels": [str(i) for i in range(len(klines))], "prices": [k["close"] for k in klines]})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/analyze/<symbol>")
def analyze(symbol):
    try:
        pair = symbol.upper()
        if not pair.endswith("USDT"):
            pair += "USDT"
        ticker = get_24h_ticker(pair)
        klines = get_klines(pair, "1h", 100)
        prices = [k["close"] for k in klines]
        volumes = [k["volume"] for k in klines]
        return api_ok({"ticker": ticker, "analysis": analyze_market(prices, volumes)})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/whales/<symbol>")
def whales(symbol):
    try:
        oi = get_open_interest(symbol.upper())
        liq = get_liquidation_clusters(symbol.upper())
        return api_ok({"oi": oi, "liquidation": liq})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/multichain")
def multichain():
    try:
        return api_ok({"report": get_multi_chain_report()})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/honeypot/<token>")
def honeypot(token):
    try:
        return api_ok({"report": check_token_safety(token)})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/signals/<chain>")
def signals(chain):
    try:
        return api_ok({"signals": get_smart_money_signals(chain.lower())})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/joint")
def joint():
    try:
        name = request.args.get("name", "购房基金")
        goal = float(request.args.get("goal", 5))
        token = request.args.get("token", "USDT")
        acc = create_joint_account(name, goal, token)
        return api_ok({"progress": acc.get_progress()})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/post/<symbol>")
def post(symbol):
    try:
        return api_ok({"post": generate_post_basic(symbol)})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/alpha")
def alpha():
    try:
        return api_ok({"report": get_alpha_signals()})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/entry-suggestion", methods=["POST"])
@auth_required
def entry_suggestion():
    try:
        payload = request.get_json(force=True) or {}
        result = build_entry_suggestion(
            symbol=str(payload.get("symbol", "BTCUSDT")),
            market_type=str(payload.get("market_type", "spot")),
            side=str(payload.get("side", "LONG")),
        )
        return api_ok(result)
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/positions", methods=["GET", "POST"])
@auth_required
def positions():
    try:
        user_id = str(request.current_user)
        if request.method == "POST":
            payload = request.get_json(force=True) or {}
            entry_price = float(payload.get("entry_price", 0))
            quantity = float(payload.get("quantity", 0))
            leverage = float(payload.get("leverage", 1))
            if entry_price <= 0 or quantity <= 0 or leverage <= 0:
                return api_ok({"error": "entry_price/quantity/leverage 必须大于0"}, 400)
            created = insert_position(
                user_id=user_id,
                market_type=str(payload.get("market_type", "spot")).lower(),
                symbol=str(payload.get("symbol", "BTCUSDT")).upper(),
                side=str(payload.get("side", "LONG")).upper(),
                entry_price=entry_price,
                quantity=quantity,
                leverage=leverage,
                stop_loss=float(payload.get("stop_loss")) if payload.get("stop_loss") is not None else None,
                take_profit_1=float(payload.get("take_profit_1")) if payload.get("take_profit_1") is not None else None,
                take_profit_2=float(payload.get("take_profit_2")) if payload.get("take_profit_2") is not None else None,
                take_profit_3=float(payload.get("take_profit_3")) if payload.get("take_profit_3") is not None else None,
                opened_at=datetime.now(timezone.utc).isoformat(),
            )
            return api_ok({"position": created}, 201)

        status = str(request.args.get("status", "OPEN")).upper()
        market_type = request.args.get("market_type", "").strip().lower() or None
        data = list_positions(user_id=user_id, status=status, market_type=market_type)
        return api_ok({"positions": data})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/positions/<int:position_id>/risk", methods=["POST"])
@auth_required
def positions_risk(position_id: int):
    try:
        payload = request.get_json(force=True) or {}
        updated = update_position_risk(
            user_id=str(request.current_user),
            position_id=position_id,
            stop_loss=float(payload.get("stop_loss")) if payload.get("stop_loss") is not None else None,
            take_profit_1=float(payload.get("take_profit_1")) if payload.get("take_profit_1") is not None else None,
            take_profit_2=float(payload.get("take_profit_2")) if payload.get("take_profit_2") is not None else None,
            take_profit_3=float(payload.get("take_profit_3")) if payload.get("take_profit_3") is not None else None,
        )
        if not updated:
            return api_ok({"error": "仓位不存在或已平仓"}, 404)
        return api_ok({"position": updated})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/positions/<int:position_id>/close", methods=["POST"])
@auth_required
def positions_close(position_id: int):
    try:
        payload = request.get_json(force=True) or {}
        closed = close_position(
            user_id=str(request.current_user),
            position_id=position_id,
            close_price=float(payload.get("close_price", 0)),
            close_reason=str(payload.get("close_reason", "manual")),
        )
        if not closed:
            return api_ok({"error": "仓位不存在或已平仓"}, 404)
        return api_ok({"position": closed})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/risk/position-size", methods=["POST"])
def risk_position_size():
    try:
        payload = request.get_json(force=True) or {}
        result = calculate_position_size(
            account_size=float(payload.get("account_size", 0)),
            risk_pct=float(payload.get("risk_pct", 0)),
            entry_price=float(payload.get("entry_price", 0)),
            stop_price=float(payload.get("stop_price", 0)),
            leverage=float(payload.get("leverage", 1)),
        )
        return api_ok(result)
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/guardrails/evaluate", methods=["POST"])
@auth_required
def guardrails_evaluate():
    try:
        payload = request.get_json(force=True) or {}
        result = evaluate_guardrail(
            user_id=str(request.current_user),
            outcome=str(payload.get("outcome", "open")),
        )
        return api_ok(result)
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/guardrails/config", methods=["GET", "POST"])
@auth_required
def guardrails_config():
    try:
        user_id = str(request.current_user)
        if request.method == "GET":
            return api_ok({"config": get_user_guardrail_config(user_id)})

        payload = request.get_json(force=True) or {}
        updated = update_user_guardrail_config(
            user_id=user_id,
            max_trades_per_day=int(payload.get("max_trades_per_day", 8)),
            cooldown_losses=int(payload.get("cooldown_losses", 3)),
            cooldown_minutes=int(payload.get("cooldown_minutes", 45)),
        )
        return api_ok({"config": updated})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/journal", methods=["GET", "POST"])
@auth_required
def journal():
    try:
        user_id = str(request.current_user)
        if request.method == "POST":
            payload = request.get_json(force=True) or {}
            saved = add_journal_entry(user_id, payload)
            return api_ok({"entry": saved}, 201)

        limit = int(request.args.get("limit", 30))
        market_type = request.args.get("market_type", "").strip().lower() or None
        return api_ok({"entries": list_journal(user_id, limit, market_type)})
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


@app.route("/api/review/daily", methods=["GET"])
@auth_required
def review_daily():
    try:
        day = request.args.get("date", "").strip() or None
        result = get_daily_review(str(request.current_user), day)
        return api_ok(result)
    except Exception as e:
        return api_ok({"error": str(e)}, 400)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    print(f"Starting Web Dashboard on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
