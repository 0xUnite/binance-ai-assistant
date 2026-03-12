# Skills 文档总览

这套 Skills 参考 Binance 官方能力拆分方式，把现有项目能力整理成 7 个相对独立的功能单元。

## 目录

1. [Market Rank](./market-rank.md)
2. [Token Info](./token-info.md)
3. [Token Audit](./token-audit.md)
4. [Trading Signal](./trading-signal.md)
5. [Spot](./spot.md)
6. [Address Info](./address-info.md)
7. [Meme Rush](./meme-rush.md)

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
