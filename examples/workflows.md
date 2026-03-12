# 工作流示例

下面这 4 个工作流参考 Binance 官方 workflows 思路，但全部映射到当前仓库已有能力。

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
