# Binance AI Assistant

Binance AI 交易助手，包含 Web 仪表盘、API 服务、Telegram Bot、CLI 助手，并新增生产级用户系统与风控持久化能力。

## 更新亮点（生产增强版）
- 修复核心运行问题与语法错误（可直接启动）
- Web 端全面重构（响应式 + 统一交互 + 错误处理）
- 新增用户系统：注册、登录、鉴权 token
- 新增 SQLite 持久化：用户、守护器配置、守护器状态、交易日志
- 新增风控能力：
  - 仓位风险计算器
  - 交易纪律守护器（交易上限/连亏冷静期）
  - 可配置守护器规则（按用户隔离）
- 新增交易日志（按用户隔离、可复盘）
- 新增仅开仓建议（现货/合约/链上统一入口，含允许开仓判断）
- 新增仓位管理（开仓、TP/SL 调整、平仓、PnL 自动计算）
- 新增每日复盘（按 spot/futures/onchain 分维度统计胜率与净盈亏）

## 功能概览
- Web 仪表盘：价格、K线、信号、巨鲸、多链、安全审计、发帖生成
- AI 助手：价格查询、市场分析、订单簿、热门代币、公告、自然语言对话
- API Server：行情、技术分析、账户查询、新闻
- Telegram Bot：命令式市场分析与交易计划

## 目录结构
```text
binance-ai-assistant/
├── ai_assistant/
├── api_server/
├── web_ui/
├── telegram_bot/
├── post_generator/
├── indicators/
├── utils/
│   ├── binance_api.py
│   ├── user_guardrails.py
│   ├── persistence.py
│   └── ...
├── data/
│   └── .gitkeep
├── requirements.txt
└── README.md
```

## 环境要求
- Python 3.10+
- pip

## 安装
```bash
git clone https://github.com/0xUnite/binance-ai-assistant.git
cd binance-ai-assistant
pip install -r requirements.txt
```

## 环境变量
可选但推荐配置：

```bash
# Web/Auth
export APP_SECRET_KEY="replace-with-a-strong-secret"

# Binance API（如需账户/交易相关能力）
export BINANCE_API_KEY="your_key"
export BINANCE_SECRET_KEY="your_secret"

# Telegram（如需启动 Bot）
export TELEGRAM_BOT_TOKEN="your_bot_token"

# SQLite 路径（可选）
export BINANCE_ASSISTANT_DB="/absolute/path/assistant.db"
```

## 启动方式

### 1) 启动 Web 仪表盘
```bash
python web_ui/main.py
```
默认地址：`http://localhost:3000`

### 2) 启动 API 服务
```bash
python api_server/main.py
```
健康检查：`GET /api/health`

### 3) 启动 CLI AI 助手
```bash
python ai_assistant/main.py
```

### 4) 启动 Telegram Bot
```bash
python telegram_bot/main.py
```

## Web 端使用说明

### 第一步：注册与登录
1. 打开页面右上角
2. 输入用户名和密码
3. 点击“注册”后再“登录”

### 第二步：使用开仓建议、仓位管理、风控与复盘
- `开仓建议` 页面：
  - 输入交易对 + 市场类型（spot/futures/onchain）+ 方向（LONG/SHORT）
  - 系统返回是否允许开仓、置信度、入场区间、止盈止损建议
- `仓位管理` 页面：
  - 创建仓位：市场、方向、入场价、数量、杠杆、TP/SL
  - 管理仓位：修改 TP/SL、一键平仓、自动计算平仓 PnL
- `风控` 页面：
  - 仓位风险计算器：根据账户规模、风险%、入场/止损自动算数量
  - 交易纪律守护器：保存规则后，按每笔结果评估是否触发冷静期
- `日志` 页面：
  - 记录市场类型、方向、结果、PnL、情绪、理由、标签
  - 自动按当前登录用户隔离
- `复盘` 页面：
  - 每日汇总总交易数、净盈亏、各市场胜率

## 新增鉴权 API（Web 后端）

### Auth
- `POST /api/auth/register`
  - body: `{ "username": "alice", "password": "secret123" }`
- `POST /api/auth/login`
  - body: `{ "username": "alice", "password": "secret123" }`
  - return: `{ "token": "...", "username": "alice" }`
- `GET /api/auth/me`
  - header: `Authorization: Bearer <token>`

### Guardrails
- `GET /api/guardrails/config`（需登录）
- `POST /api/guardrails/config`（需登录）
  - body: `{ "max_trades_per_day": 8, "cooldown_losses": 3, "cooldown_minutes": 45 }`
- `POST /api/guardrails/evaluate`（需登录）
  - body: `{ "outcome": "win|loss|open" }`

### Entry Suggestion（仅开仓建议）
- `POST /api/entry-suggestion`（需登录）
  - body: `{ "symbol":"BTCUSDT", "market_type":"spot|futures|onchain", "side":"LONG|SHORT" }`
  - return: `allow_open/confidence/entry_zone/risk_plan`

### Positions（仓位管理）
- `POST /api/positions`（需登录）
  - body: `{ "market_type":"futures", "side":"LONG", "symbol":"BTCUSDT", "entry_price":65000, "quantity":0.01, "leverage":3, "stop_loss":64000, "take_profit_1":66000, "take_profit_2":67000, "take_profit_3":68000 }`
- `GET /api/positions?status=OPEN|CLOSED&market_type=spot|futures|onchain`（需登录）
- `POST /api/positions/<id>/risk`（需登录）
  - body: `{ "stop_loss":64500, "take_profit_1":66200, "take_profit_2":67500, "take_profit_3":69000 }`
- `POST /api/positions/<id>/close`（需登录）
  - body: `{ "close_price":66100, "close_reason":"manual|tp|sl" }`

### Journal
- `POST /api/journal`（需登录）
  - body: `{ "symbol":"BTCUSDT", "side":"BUY", "market_type":"futures", "result":"win|loss|open", "pnl":120.5, "thesis":"breakout", "emotion":"calm", "tags":["breakout"] }`
- `GET /api/journal?limit=20&market_type=spot|futures|onchain`（需登录）

### Daily Review
- `GET /api/review/daily?date=YYYY-MM-DD`（需登录）

## 数据持久化说明
- 默认数据库文件：`data/assistant.db`
- 已通过 `.gitignore` 忽略运行时数据库文件
- 支持通过 `BINANCE_ASSISTANT_DB` 自定义路径

## 常见问题

### 1) `ModuleNotFoundError`
请从项目根目录执行命令：
```bash
cd binance-ai-assistant
python web_ui/main.py
```

### 2) Binance 请求失败
- 检查网络
- 检查交易对是否正确（例如 `BTCUSDT`）
- 部分接口会因权限或区域限制返回错误

### 3) 登录后接口仍 401
- 确认请求头带 `Authorization: Bearer <token>`
- 确认 `APP_SECRET_KEY` 没有在运行中被修改

## 风险提示
- 本项目仅作研究与演示，不构成投资建议
- 数字资产波动剧烈，请严格控制风险
