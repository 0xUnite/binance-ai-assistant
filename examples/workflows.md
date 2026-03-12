# 工作流示例

下面这 8 个工作流参考 Binance 官方 workflows 思路，并映射到当前仓库已有能力与可扩展方向。

---

## 1. Daily Briefing（日常市场简报）

### 目标
在 1~2 分钟内给用户一个“今天市场该先看什么”的摘要。

### 组合 Skills
- Market Rank
- Token Info
- Trading Signal
- Meme Rush

### 推荐步骤
1. 用 **Market Rank** 拉取今日热门榜前 10
2. 选出 BTC / ETH + 2 个高热度山寨币
3. 用 **Token Info** 提取基础行情
4. 用 **Trading Signal** 生成短线偏向
5. 用 **Meme Rush** 补充链上热点和情绪
6. 输出一份晨报/晚报

### 示例输出骨架
- 大盘一句话
- 热门榜前 5
- 今日重点关注 3 币
- 风险提醒

---

## 2. Deep Dive（单币深度研究）

### 目标
对一个币做从行情到风险的完整拆解。

### 组合 Skills
- Token Info
- Trading Signal
- Token Audit
- Spot

### 推荐步骤
1. `Token Info`：获取价格、涨跌、成交额
2. `Trading Signal`：看趋势、RSI、MACD、关键位
3. `Token Audit`：检查 honeypot / 安全风险
4. `Spot`：如果要交易，给出仓位与执行建议
5. 汇总成“能不能做、怎么做、做错怎么办”

### 适合场景
- 用户问：`帮我深度分析一下 DOGE`
- 用户问：`这个币能不能买`

---

## 3. On-Chain Intel（链上情报）

### 目标
把多链热点、地址线索与资金异动整合成一页情报。

### 组合 Skills
- Address Info
- Meme Rush
- Token Audit

### 推荐步骤
1. `Address Info`：识别地址/代币相关链上信息
2. `Meme Rush`：判断是否属于当前热点轮动
3. `Token Audit`：做快速风险排雷
4. 输出“线索级”研判，而不是过度确定的结论

### 适合场景
- 新地址突然活跃
- 某链出现短时热点爆发
- Smart Money / KOL 动向跟踪

---

## 4. Meme Hunter（Meme 狩猎）

### 目标
高效率筛选值得继续跟踪的小币和 meme 机会。

### 组合 Skills
- Meme Rush
- Market Rank
- Token Audit
- Trading Signal

### 推荐步骤
1. `Meme Rush`：先拉候选池
2. `Market Rank`：确认是否有量能支持
3. `Token Audit`：筛掉高风险标的
4. `Trading Signal`：判断入场节奏
5. 输出观察清单：A 级继续研究，B 级观察，C 级放弃

### 示例分级
- **A 级**：有量、有叙事、风险可控
- **B 级**：有热度但结构一般
- **C 级**：明显高风险或缺乏流动性

---

## 如何在现有产品里落地

### Telegram Bot
- `/top` → Market Rank
- `/token BTC` → Token Info
- `/analyze BTC` → Trading Signal
- `/trade BTC` → Trading Signal + Spot

### Web UI
- Dashboard → Daily Briefing 首页
- Alpha / Multi / Copy → On-Chain Intel / Meme Hunter
- Safety → Token Audit

### API Server
后续可以把工作流封装成组合接口，例如：
- `/api/workflows/daily-briefing`
- `/api/workflows/deep-dive/<symbol>`
- `/api/workflows/onchain-intel/<address>`
- `/api/workflows/meme-hunter?chain=solana`
- `/api/workflows/alpha-scout?limit=20`
- `/api/workflows/futures-execution/<symbol>`
- `/api/workflows/margin-playbook/<symbol>`
- `/api/workflows/asset-ops-overview`

---

## 5. Alpha Scout（Alpha 市场雷达）

### 目标
围绕 Binance 最新的 Alpha 市场数据能力，快速筛出值得继续研究的候选币。

### 组合 Skills
- Alpha Market Data
- Market Rank
- Trading Signal
- Token Audit

### 推荐步骤
1. `Alpha Market Data`：拉取 Alpha 候选池、24h 统计和 K 线
2. `Market Rank`：确认是否同时具备市场关注度与成交额
3. `Trading Signal`：判断趋势、节奏和关键位
4. `Token Audit`：对高风险小币做快速排雷
5. 输出观察池：立即研究 / 继续观察 / 放弃

### 适合场景
- 用户问：`最近 Binance Alpha 有什么值得看？`
- 做活动演示时，需要快速展示“从发现到筛选”的完整链路

---

## 6. Futures Execution Planner（U 本位合约执行规划）

### 目标
把 U 本位合约的市场数据、资金费率和风控建议整合成一份可执行计划。

### 组合 Skills
- Alpha Market Data
- Trading Signal
- USDⓈ-M Futures Trading

### 推荐步骤
1. `Alpha Market Data`：看最近走势和成交热度
2. `Trading Signal`：确定偏多/偏空与关键支撑阻力
3. `USDⓈ-M Futures Trading`：补充标记价、资金费率、保证金需求和杠杆建议
4. 生成计划：方向、仓位、止损、止盈、失效条件
5. 若接真实交易，优先测试网验证

### 适合场景
- 用户问：`帮我做一份 BTCUSDT 的 U 本位合约计划`
- 比赛答辩时展示“数据 + 信号 + 风控”闭环

---

## 7. Margin Playbook（杠杆交易作战手册）

### 目标
为全仓/逐仓杠杆交易生成安全边界清晰的操作方案。

### 组合 Skills
- Token Info
- Trading Signal
- Margin Trading
- Asset Management

### 推荐步骤
1. `Token Info`：确认标的和基础波动情况
2. `Trading Signal`：判断是否值得做以及怎么做
3. `Margin Trading`：计算保证金需求、建议杠杆、逐仓/全仓模式
4. `Asset Management`：核对账户是否有足够且合理的资产配置
5. 输出最终建议：不开单 / 小仓逐仓 / 谨慎全仓

### 适合场景
- 用户问：`这单用逐仓还是全仓更合适？`
- 需要把“想做”转成“能不能安全地做”

---

## 8. Asset Ops Overview（资产管理总览）

### 目标
把账户余额、资产分布、手续费优化和潜在资产操作入口整合成一页总览。

### 组合 Skills
- Asset Management
- Spot
- USDⓈ-M Futures Trading

### 推荐步骤
1. `Asset Management`：读取余额、估值和持仓集中度
2. 标记主要资产、闲置资产和高风险敞口
3. `Spot`：如果需要做现货调仓，生成执行建议
4. `USDⓈ-M Futures Trading`：如果有合约暴露，补充风险视角
5. 输出账户建议：保持 / 降风险 / 调仓 / 继续观察

### 适合场景
- 用户问：`帮我看下账户现在健康吗？`
- 演示统一资产视图与风险提示能力
