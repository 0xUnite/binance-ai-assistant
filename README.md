# Binance AI Assistant

Binance AI 交易助手，包含 **Web 仪表盘、API 服务、Telegram Bot、CLI 助手**，并在现有生产增强能力基础上，进一步整理出 **Binance 风格的 Skills、工作流与 Prompt 预设**，方便评审理解与后续 Agent 集成。

> 这版 README 不是把旧内容推倒重来，而是把“生产增强版能力”与“参赛包装层”合并到一起。该保留的保留，该补的补，少一点花架子，多一点结构感。

## 更新亮点

### 生产增强能力
- 修复核心运行问题与语法错误（可直接启动）
- Web 端重构（响应式 + 统一交互 + 错误处理）
- 新增用户系统：注册、登录、鉴权 token
- 新增 SQLite 持久化：用户、守护器配置、守护器状态、交易日志
- 新增风控能力：
  - 仓位风险计算器
  - 交易纪律守护器（交易上限 / 连亏冷静期）
  - 可配置守护器规则（按用户隔离）
- 新增交易日志与每日复盘
- 集成 DumpDetective：一键出货风险扫描

### 参赛包装增强
- 新增 **11 个 Binance 风格 Skills 文档**
- 其中补齐 Binance 最新公告提到的 **4 个新能力**：
  - **Alpha Market Data**：代币列表、交易信息、K 线、24h 统计
  - **USDⓈ-M Futures Trading**：合约市场数据、资金费率、标记价格、订单簿、交易执行规划
  - **Margin Trading**：全仓/逐仓杠杆决策、保证金预算、风险约束
  - **Asset Management**：账户余额、资产总览、充提/手续费/碎币转换入口设计
- 新增 **8 个工作流示例**（原 4 个 + Alpha Scout / Futures Execution Planner / Margin Playbook / Asset Ops Overview）
- 新增 **Prompt Presets**，方便接入 Bot / Agent / API workflow
- README 重新整理为更专业的产品文档结构
- 新增 `.gitignore` 与 `SECURITY.md`，强化密钥与运行时文件保护

## 与 Binance Skills 的映射

| Binance 官方方向 | 本项目对应能力 |
|---|---|
| Market Rank | `skills/market-rank.md` + `get_top_coins()` + Web Dashboard 热门榜 |
| Token Info | `skills/token-info.md` + `/token` + `/api/ticker/<symbol>` |
| Token Audit | `skills/token-audit.md` + `utils/honeypot_detector.py` |
| Trading Signal | `skills/trading-signal.md` + `indicators/` + `signal-alerts/` |
| Spot | `skills/spot.md` + `utils/binance_api.py` + 账户/下单相关能力 |
| Address Info | `skills/address-info.md` + 多链扫描 / 链上扩展接口 |
| Meme Rush | `skills/meme-rush.md` + `multi_chain_scanner` + `alpha_radar` |
| **Alpha Market Data（新增）** | `skills/alpha-market-data.md` + `get_binance_alpha_tokens()` / `get_24h_ticker()` / `get_klines()` |
| **USDⓈ-M Futures Trading（新增）** | `skills/usdt-m-futures.md` + `FUTURES_BASE_URL` / `get_funding_rate()` / futures 风控与计划逻辑 |
| **Margin Trading（新增）** | `skills/margin-trading.md` + `user_guardrails` / `trading_advisor` / 账户视图 |
| **Asset Management（新增）** | `skills/asset-management.md` + `get_account_balance()` / `portfolio-tracker` / `/api/balance` |
| Daily Briefing | `examples/workflows.md` |
| Deep Dive | `examples/workflows.md` |
| On-Chain Intel | `examples/workflows.md` |
| Meme Hunter | `examples/workflows.md` |
| **Alpha Scout（新增）** | `examples/workflows.md` |
| **Futures Execution Planner（新增）** | `examples/workflows.md` |
| **Margin Playbook（新增）** | `examples/workflows.md` |
| **Asset Ops Overview（新增）** | `examples/workflows.md` |

## 新增 4 个 Binance 能力，一眼看懂

### 1. Alpha Market Data
- Alpha 候选代币列表
- 单币交易信息、24h 统计
- K 线图与热度观察
- 适合作为“发现 → 分析”的第一步

### 2. USDⓈ-M Futures Trading
- 合约市场数据、订单簿、资金费率、标记价格
- 合约交易计划：方向、杠杆、止损、止盈
- 支持主网 / 测试网的接入设计说明
- 当前仓库更偏“数据 + 风控 + 执行规划”能力

### 3. Margin Trading
- 全仓 / 逐仓杠杆模式决策
- 保证金预算与风险约束
- 杠杆交易工作流骨架
- 为借还款、OCO / OTO / OTOCO 等扩展预留接口空间

### 4. Asset Management
- 账户余额、持仓估值、资产集中度
- 充提、BNB 抵扣、碎币转换等入口设计
- 适合作为现货、合约、杠杆前的统一资产视图
- 默认强调只读优先与禁止提现权限

## 功能概览

### 1. 市场与行情
- 实时价格、24h 行情、K 线、订单簿、资金费率
- 热门币种排行
- Open Interest、市场情绪、清算区间等衍生数据

### 2. 分析与信号
- RSI / MACD / MA / 布林带
- 趋势识别与买卖信号
- 交易计划生成（入场、止损、目标位、DCA）
- 价格阈值提醒与 Telegram 推送

### 3. 风险与链上扩展
- Honeypot / 代币安全检查
- 多链热点扫描（Solana / BSC / Base 等）
- Alpha Radar / Smart Money 信号
- DumpDetective 出货风险扫描

### 4. 资产与执行
- 账户余额、持仓跟踪、组合视图
- Spot / Futures / On-chain 统一开仓建议入口
- 仓位管理、止盈止损调整、平仓与 PnL 计算
- 回测与策略比较

### 5. 内容与增长
- 市场简报生成
- 推文 / Thread 生成
- 教育内容与解释型回答

## 当前代码结构

```text
binance-ai-assistant/
├── ai_assistant/         # 自然语言助手入口
├── api_server/           # Flask REST API
├── backtest/             # 策略回测引擎
├── crypto-educator/      # 教育/解释型输出
├── indicators/           # RSI / MACD / MA 等指标
├── portfolio-tracker/    # 账户与资产跟踪
├── post_generator/       # 市场观点与推文生成
├── signal-alerts/        # Telegram 价格提醒
├── telegram_bot/         # Bot 命令交互
├── trading-bot/          # 交易执行与策略入口
├── utils/                # Binance API、多链扫描、风控、持久化、辅助函数
├── web_ui/               # Web 仪表盘
├── data/                 # SQLite / 运行时数据
├── skills/               # 新增：Skill 文档
├── examples/             # 新增：工作流示例
└── prompts/              # 新增：Prompt 预设
```

## 安装

```bash
git clone https://github.com/0xUnite/binance-ai-assistant.git
cd binance-ai-assistant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 环境变量

推荐通过 `.env` 或部署平台 Secret 配置。

```bash
# Web/Auth
export APP_SECRET_KEY="replace-with-a-strong-secret"

# Binance API（如需账户/交易相关能力）
export BINANCE_API_KEY="your_key"
export BINANCE_SECRET_KEY="your_secret"

# OpenAI（如需 AI 增强）
export OPENAI_API_KEY="your_openai_key"

# Telegram（如需启动 Bot / 提醒）
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"

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

### 5) 启动其他模块
```bash
python backtest/main.py BTCUSDT
python portfolio-tracker/main.py
python signal-alerts/main.py
python post_generator/main.py BTC
```

## Web 端使用说明

### 第一步：注册与登录
1. 打开页面右上角
2. 输入用户名和密码
3. 点击“注册”后再“登录”

### 第二步：使用开仓建议、仓位管理、风控与复盘
- `出货侦探` 页面：
  - 输入合约地址（creator 地址可选）即可自动完成多维扫描
  - 输出统一 `LOW / MEDIUM-HIGH / HIGH` 风险评级和证据
- `开仓建议` 页面：
  - 输入交易对 + 市场类型（spot / futures / onchain）+ 方向（LONG / SHORT）
  - 返回是否允许开仓、置信度、入场区间、止盈止损建议
- `仓位管理` 页面：
  - 创建仓位：市场、方向、入场价、数量、杠杆、TP / SL
  - 管理仓位：修改 TP / SL、一键平仓、自动计算平仓 PnL
- `风控` 页面：
  - 仓位风险计算器：根据账户规模、风险%、入场/止损自动算数量
  - 交易纪律守护器：保存规则后，按每笔结果评估是否触发冷静期
- `日志` 页面：
  - 记录市场类型、方向、结果、PnL、情绪、理由、标签
  - 自动按当前登录用户隔离
- `复盘` 页面：
  - 每日汇总总交易数、净盈亏、各市场胜率

## 新增文档资产

### Skills
- `skills/market-rank.md`
- `skills/token-info.md`
- `skills/token-audit.md`
- `skills/trading-signal.md`
- `skills/spot.md`
- `skills/address-info.md`
- `skills/meme-rush.md`
- `skills/alpha-market-data.md`
- `skills/usdt-m-futures.md`
- `skills/margin-trading.md`
- `skills/asset-management.md`
- `skills/README.md`

### Workflows
- `examples/workflows.md`

### Prompt Presets
- `prompts/presets.md`

这些文档的意义：
1. 给评委快速理解项目能力边界
2. 给后续 Agent / Bot 做能力路由
3. 给开发者扩展工作流时提供统一模板

## 新增鉴权 API（Web 后端）

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Guardrails
- `GET /api/guardrails/config`（需登录）
- `POST /api/guardrails/config`（需登录）
- `POST /api/guardrails/evaluate`（需登录）

### Entry Suggestion（仅开仓建议）
- `POST /api/entry-suggestion`（需登录）

### Positions（仓位管理）
- `POST /api/positions`（需登录）
- `GET /api/positions?status=OPEN|CLOSED&market_type=spot|futures|onchain`（需登录）
- `POST /api/positions/<id>/risk`（需登录）
- `POST /api/positions/<id>/close`（需登录）

### Journal
- `POST /api/journal`（需登录）
- `GET /api/journal?limit=20&market_type=spot|futures|onchain`（需登录）

### Daily Review
- `GET /api/review/daily?date=YYYY-MM-DD`（需登录）

### DumpDetective Integration
- `POST /api/dump-detective/scan`

## API 示例

```bash
curl http://localhost:3000/api/health
curl http://localhost:3000/api/ticker/BTCUSDT
curl "http://localhost:3000/api/analysis/BTCUSDT?interval=1h"
curl "http://localhost:3000/api/top?limit=10"
```

## 数据持久化说明

- 默认数据库文件：`data/assistant.db`
- 已通过 `.gitignore` 忽略运行时数据库文件
- 支持通过 `BINANCE_ASSISTANT_DB` 自定义路径

## 安全与密钥管理

本仓库已按以下原则整理：

- **不在文档、示例或代码中暴露真实 API Key**
- **默认通过环境变量注入密钥**
- **`.gitignore` 已忽略 `.env`、数据库、缓存与 Python 编译文件**
- README、`.env.example` 和各子模块文档中仅保留占位符，不放真实凭证
- 资产管理、现货、合约、杠杆相关说明里统一强调：**不要开启提现权限**

建议：
1. Binance API 仅开启读取或最小必要交易权限
2. **不要开启提现权限**
3. 为 Bot / 自动化账号单独创建 API Key
4. 生产环境把密钥放到 CI/CD Secret 或部署平台 Secret Manager
5. 对真实下单、借贷、资产划转等能力增加二次确认与审计日志

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

## 已识别的后续优化点

- `telegram_bot/main.py` 中自然语言分发逻辑还比较基础，可升级为真正的 Skill Router
- `web_ui/main.py` 把 HTML 与后端写在一个文件中，后续可拆成模板与 API 层
- 部分模块仍偏 demo / 原型风格，适合继续补测试、异常处理和类型约束
- 可把 Skills 与 API endpoint 抽成统一 schema，方便函数调用和 MCP / Agent 集成

## 风险提示

- 本项目仅作研究、教育与演示，不构成投资建议
- 数字资产波动剧烈，请严格控制风险
- 策略回测不代表未来表现
- 自动化交易前请先用小额、只读或模拟环境验证

## License

如无额外声明，遵循仓库当前开源协议与上游依赖协议。