# Skills 文档总览

这套 Skills 参考 Binance 官方能力拆分方式，把现有项目能力整理成 **11 个**相对独立的功能单元：既覆盖原有的行情、审计、信号与现货能力，也补上了 Binance 最新公告提到的 4 个新方向。

## 目录

1. [Market Rank](./market-rank.md)
2. [Token Info](./token-info.md)
3. [Token Audit](./token-audit.md)
4. [Trading Signal](./trading-signal.md)
5. [Spot](./spot.md)
6. [Address Info](./address-info.md)
7. [Meme Rush](./meme-rush.md)
8. [Alpha Market Data](./alpha-market-data.md)
9. [USDⓈ-M Futures Trading](./usdt-m-futures.md)
10. [Margin Trading](./margin-trading.md)
11. [Asset Management](./asset-management.md)

## 设计原则

- **单一职责**：一个 Skill 解决一类问题
- **可组合**：多个 Skill 可以串成工作流
- **可落地**：尽量映射到现有代码，而不是空概念
- **风险可解释**：涉及交易和风控时必须明确边界

## 推荐路由

- 市场概览 / 热门榜 → Market Rank
- 单币查询 / 基础数据 → Token Info
- 安全检查 / Honeypot → Token Audit
- 技术分析 / 买卖信号 → Trading Signal
- 余额 / 下单 / 现货执行 → Spot
- 地址 / 链上动向 / 多链资产 → Address Info
- 热点挖掘 / 小币 / Meme 轮动 → Meme Rush
- Alpha 候选池 / K 线 / 24h 统计 → Alpha Market Data
- U 本位合约行情 / 资金费率 / 合约执行计划 → USDⓈ-M Futures Trading
- 杠杆预算 / 全仓逐仓决策 / 借贷前检查 → Margin Trading
- 账户总览 / 余额估值 / 资产操作入口 → Asset Management
