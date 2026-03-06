# Binance AI Assistant

🤖 功能强大的 Binance 智能助手

## 🆕 v3.0 - AI Agent 版 (参赛版本)

基于 OpenClaw AI Framework 构建，提供全方位的 Binance 服务支持。

## ✨ 功能特性

### 📊 市场数据查询
- ✅ 实时价格查询
- ✅ 24小时行情数据
- ✅ K线数据（多时间周期）
- ✅ 订单簿深度
- ✅ 最新成交记录
- ✅ 资金费率查询
- ✅ 币安Alpha热门代币

### 💱 交易辅助
- ✅ 技术指标分析 (RSI, MACD, MA)
- ✅ 市场趋势判断
- ✅ 交易信号生成
- ✅ 交易规则查询
- ✅ 手续费率查询

### 🤖 AI 智能对话
- ✅ 自然语言查询市场数据
- ✅ 智能交易建议
- ✅ 风险提示
- ✅ 投资组合分析

### 📈 交易机器人
- ✅ RSI 策略自动交易
- ✅ 止损止盈保护
- ✅ 仓位管理
- ✅ 交易日志

### 🔔 价格提醒
- ✅ 价格到达提醒
- ✅ Telegram 推送
- ✅ 多币种监控

### 💼 组合追踪
- ✅ 实时余额查询
- ✅ 盈亏计算
- ✅ 资产分布

## 🚀 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/0xUnite/binance-ai-assistant.git
cd binance-ai-assistant

# 安装依赖
pip install -r requirements.txt
```

### 配置环境变量

```bash
# 创建 .env 文件
cp .env.example .env

# 编辑 .env，填入你的 API Keys
BINANCE_API_KEY=your_api_key
BINANCE_SECRET_KEY=your_secret_key
OPENAI_API_KEY=your_openai_key  # 可选
TELEGRAM_BOT_TOKEN=your_token   # 可选
TELEGRAM_CHAT_ID=your_chat_id   # 可选
```

### 启动服务

```bash
# 启动 AI 助手 (交互式)
python ai_assistant/main.py

# 启动交易机器人
python trading-bot/main.py

# 启动价格提醒
python signal-alerts/main.py

# 查看组合
python portfolio-tracker/main.py

# 启动 API 服务
python api_server/main.py
```

## 📁 项目结构

```
binance-ai-assistant/
├── ai_assistant/         # 🤖 AI 智能助手
│   ├── main.py
│   └── prompts.py
├── api_server/           # 🌐 REST API 服务
│   └── main.py
├── trading-bot/          # 📈 交易机器人
│   └── main.py
├── signal-alerts/        # 🔔 价格提醒
│   └── main.py
├── portfolio-tracker/    # 💼 组合追踪
│   └── main.py
├── crypto_educator/      # 📚 加密教育
│   └── main.py
├── indicators/           # 📊 技术指标库
│   └── indicators.py
├── utils/                # 🔧 工具函数
│   └── binance_api.py
└── requirements.txt
```

## 🤖 AI 助手使用示例

```
❓ 你: BTC 现在多少钱？

🤖 AI: BTC 目前价格 $70,500，24小时涨幅 +2.3%

❓ 你: 给我看看 ETH 的技术分析

🤖 AI: ETH/USDT 技术分析:
- RSI(14): 65.4 (中性偏强)
- MACD: 金叉信号
- MA(20): $3,450 (支撑位)
- 趋势: 偏强，建议观望

❓ 你: 有什么 Alpha 币推荐？

🤖 AI: 当前币安 Alpha 热门:
1. $DEEP - 涨幅 25%
2. $VELA - 涨幅 18%
3. $RIX - 涨幅 12%
```

## 📡 API 接口

### 市场数据

```bash
# 查询价格
GET /api/price/BTCUSDT

# 24小时行情
GET /api/ticker/BTCUSDT

# K线数据
GET /api/klines/BTCUSDT?interval=1h&limit=100

# 订单簿
GET /api/depth/BTCUSDT

# 资金费率
GET /api/funding/BTCUSDT
```

### 技术分析

```bash
# 市场分析
GET /api/analysis/BTCUSDT
```

## 🤝 竞赛参赛说明

本项目是为 Binance AI Assistant 竞赛 (2026年3月) 开发。

**特色亮点：**
1. 基于 OpenClaw 框架，原生支持 Claude AI
2. 完整的技术指标分析 (RSI, MACD, MA)
3. 实时市场数据 + AI 智能对话
4. 可扩展的 API 服务架构

## 📄 许可证

MIT License

## ⚠️ 风险提示

本项目所有交易建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。
