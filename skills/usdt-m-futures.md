# Skill: USDⓈ-M Futures Trading

## 目标
围绕 U 本位合约交易提供市场数据、订单簿、资金费率、标记价格、持仓量视角以及下单/撤单/改单、杠杆管理、仓位模式与算法单的扩展设计。

## 对应代码
- `utils/binance_api.py` → `FUTURES_BASE_URL` / `get_funding_rate()` / `get_depth()`
- `utils/whale_tracker.py` → Open Interest / futures 数据扩展
- `utils/trading_advisor.py` → `market == "futures"` 的交易计划逻辑
- `utils/user_guardrails.py` → 杠杆、保证金、风险约束
- `web_ui/main.py` → futures 市场开仓建议 / 仓位管理 / 风控面板

## 适用场景
- 查看某个 U 本位合约的资金费率、标记价与订单簿
- 生成合约交易计划：方向、入场、止损、目标位、杠杆
- 在主网或测试网交易能力接入前，先做策略验证和风险管控

## 输入
- `symbol`：如 `BTCUSDT`
- `interval`：如 `15m` / `1h` / `4h`
- `side`：LONG / SHORT
- `leverage`
- 可选：`environment` = mainnet / testnet

## 输出
- 标记价格 / 指数价格 / 资金费率
- 订单簿摘要
- 趋势与交易计划
- 保证金需求、风险暴露、止损建议
- 后续执行建议：观望 / 小仓试单 / 条件触发

## 推荐搭配
- `Alpha Market Data`：先看热度与基本走势
- `Trading Signal`：确定节奏与关键位
- `USDⓈ-M Futures Trading`：输出合约级执行计划
- `user_guardrails`：限制过度杠杆和连亏冲动

## 当前实现边界
当前仓库已覆盖一部分 U 本位合约核心数据与合约交易计划逻辑，适合比赛展示“市场数据 + 风控驱动执行”的方向；真实的下单、撤单、改单、仓位模式和算法单仍建议继续扩展为独立 API 封装，并在测试网先验证。

## 风险提示
- 合约交易会放大收益，也会放大亏损
- 默认应先用测试网、小仓位、低杠杆验证
- 没有明确止损的合约单，本质上就是裸奔
