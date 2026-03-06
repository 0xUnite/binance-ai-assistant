# Binance AI Assistant 🤖

功能强大的 Binance 智能交易助手

## 🆕 v3.1 - 参赛版本 (Telegram + 巨鲸追踪)

基于 OpenClaw AI Framework 构建，提供全方位的 Binance 交易支持。

## ✨ 功能特性

### 📝 AI Post 生成器 (新增!)
- ✅ 一键生成市场分析推文
- ✅ 支持 AI 增强版本
- ✅ 支持 Twitter 推文串
- ✅ 包含实时数据 + 技术指标 + 巨鲸动向

### 🌐 Web 仪表盘 (新增!)
- ✅ 实时价格展示
- ✅ K线图表 (Chart.js)
- ✅ 技术信号显示
- ✅ 热门代币排行
- ✅ 响应式设计

### 🔬 策略回测 (新增!)
- ✅ RSI 策略回测
- ✅ MA 交叉策略回测
- ✅ MACD 策略回测
- ✅ 收益率统计
- ✅ 胜率统计
- ✅ 最大回撤计算

### 🐋 真实巨鲸数据 (增强!)
- ✅ Open Interest 实时数据
- ✅ 多空比分析
- ✅ 资金费率监控
- ✅ 清算区域计算
- ✅ 大额交易追踪

### 🔗 多链热点扫描 (新增!)
- ✅ Solana 热点代币
- ✅ BSC 热点代币
- ✅ Base 热点代币
- ✅ 实时行情监控

### 🔐 代币安全审计 (新增!)
- ✅ Honeypot 检测
- ✅ 合约安全分析
- ✅ 流动性检查
- ✅ 黑名单检测
- ✅ 批量扫描

### 🎮 模拟交易 (新增!)
- ✅ 虚拟买入/卖出
-实时计算
- ✅ 盈亏 ✅ 交易历史记录
- ✅ RSI 策略回测
- ✅ 风险提示

### 🔗 OKX OnchainOS 集成 (新增!)
- ✅ 0% 服务费交易
- ✅ 智能钱信号追踪
- ✅ 免签名交易 (approve + swap)
- ✅ DEX 聚合报价
- ✅ 多链支持 (ETH/BSC/Base/SOL)
- `/start` - 启动菜单
- `/portfolio` - 查看仓位
- `/balance` - 账户余额
- `/analyze BTC` - 市场分析
- `/token ETH` - 代币信息
- `/trade SOL` - 交易计划
- `/top` - 热门代币
- `/funds` - 资金信息
- 自然语言对话支持

### 📊 市场数据查询
- ✅ 实时价格查询
- ✅ 24小时行情数据
- ✅ K线数据 (多时间周期)
- ✅ 订单簿深度
- ✅ 资金费率查询
- ✅ 热门代币排行

### 🐋 巨鲸追踪 (新增!)
- ✅ Open Interest 持仓分析
- ✅ 大额转账监控
- ✅ 流动性区域 (清算集群)
- ✅ 多空比分析
- ✅ 资金费率情绪

### 📈 技术分析
- ✅ RSI 指标
- ✅ MACD 指标
- ✅ MA 移动平均线
- ✅ 布林带
- ✅ 市场趋势判断
- ✅ 交易信号生成

### 💰 仓位管理 (新增!)
- ✅ 实时盈亏追踪
- ✅ 止损止盈设置
- ✅ 历史交易记录
- ✅ 胜率统计
- ✅ DCA 补仓策略

### 🎯 交易计划生成 (新增!)
- ✅ 入场区间推荐
- ✅ 止损位设置
- ✅ DCA 补仓位
- ✅ 目标盈利位
- ✅ 建议杠杆

## 🚀 快速开始

### 安装

```bash
git clone https://github.com/0xUnite/binance-ai-assistant.git
cd binance-ai-assistant
pip install -r requirements.txt
```

### 配置

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env 文件
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
TELEGRAM_BOT_TOKEN=your_telegram_token
OPENAI_API_KEY=your_openai_key  # 可选
```

### 启动

```bash
# Telegram Bot (推荐)
python telegram_bot/main.py

# AI 助手
python ai_assistant/main.py

# API 服务
python api_server/main.py
```

## 📁 项目结构

```
binance-ai-assistant/
├── telegram_bot/          # 🤖 Telegram Bot
├── ai_assistant/          # 🤖 AI 智能助手
├── api_server/            # 🌐 REST API
├── web_ui/                # 🌐 Web 仪表盘 (新增!)
│   └── main.py
├── post_generator/        # 📝 AI Post 生成器
├── trading-bot/           # 📈 交易机器人
├── backtest/              # 🔬 策略回测 (新增!)
│   └── main.py
├── signal-alerts/         # 🔔 价格提醒
├── portfolio-tracker/     # 💼 组合追踪
├── indicators/            # 📊 技术指标库
├── utils/
│   ├── binance_api.py     # Binance API
│   ├── whale_tracker.py   # 🐋 巨鲸追踪
│   ├── whale_data.py      # 🐋 真实数据
│   ├── position_tracker.py # 💰 仓位追踪
│   ├── multi_chain_scanner.py # 🔗 多链扫描
│   ├── honeypot_detector.py   # 🔐 代币审计
│   ├── sim_trading.py     # 🎮 模拟交易
│   └── okx_onchain.py    # 🔗 OKX OnchainOS (新增!)
└── requirements.txt
```

## 🐋 巨鲸追踪示例

```python
from utils.whale_tracker import get_whale_report, get_open_interest

# 获取 BTC 巨鲸报告
print(get_whale_report("BTC"))

# 输出:
# 🐋 BTC 巨鲸分析
# 
# 📊 合约持仓 (OI)
# 总持仓: $15.6B
# 24h变化: +5.2%
# 多空比: 52.3% / 47.7%
# 
# 🎭 市场情绪: 🟢 Bullish
```

## 💰 仓位追踪示例

```python
from utils.position_tracker import PositionTracker

tracker = PositionTracker("user123")

# 开仓
tracker.open_position("BTCUSDT", 68000, 0.1, leverage=3, stop_loss=65000)

# 查看持仓
prices = {"BTCUSDT": 70000}
print(tracker.get_positions_summary(prices))

# 平仓
trade = tracker.close_position("BTCUSDT", 71000, "take_profit")
print(f"盈亏: ${trade['pnl']:+.2f}")
```

## 📡 API 接口

```bash
# 市场数据
GET /api/price/BTCUSDT
GET /api/ticker/BTCUSDT
GET /api/klines?symbol=BTCUSDT&interval=1h
GET /api/depth/BTCUSDT
GET /api/top

# 技术分析
GET /api/analysis/BTCUSDT
GET /api/rsi/BTCUSDT
GET /api/macd/BTCUSDT
```

## 🤝 竞赛参赛说明

**特色亮点：**
1. 🤖 基于 OpenClaw 框架的 Telegram Bot
2. 🐋 巨鲸活动追踪 + OI 持仓分析
3. 📈 专业技术指标 (RSI, MACD, MA, BB)
4. 💰 完整仓位管理系统
5. 🎯 AI 交易计划生成

## ⚠️ 风险提示

- 本项目所有交易建议仅供参考
- 不构成投资建议
- 投资有风险，入市需谨慎
- 请只在可承受损失的资金范围内交易

## 📄 许可证

MIT License
