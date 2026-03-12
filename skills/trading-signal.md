# Skill: Trading Signal

## 目标
基于行情与技术指标生成可执行的交易观点与计划。

## 对应代码
- `indicators/indicators.py`
- `telegram_bot/main.py` → `/analyze` / `/trade`
- `api_server/main.py` → `/api/analysis/<symbol>` / `/api/rsi/<symbol>` / `/api/macd/<symbol>`
- `signal-alerts/main.py`
- `backtest/main.py`

## 适用场景
- 这个币现在偏多还是偏空？
- 给我一个入场、止损、止盈计划
- 监控突破 / 跌破并提醒我

## 输入
- `symbol`
- `interval`：如 15m / 1h / 4h / 1d
- 可选：风险偏好（保守 / 中性 / 激进）

## 输出
- 趋势判断
- RSI / MACD / MA 等核心指标
- 信号：买入 / 卖出 / 观望
- 交易计划：入场区间、止损、目标位、DCA 位
- 风险提示

## 推荐回答结构
1. 市场状态
2. 技术指标摘要
3. 执行计划
4. 风险与失效条件

## 风险提示
- 信号是概率工具，不是保证盈利
- 必须结合仓位管理和风控
