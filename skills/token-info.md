# Skill: Token Info

## 目标
针对单个币种输出结构化基础信息，包括价格、涨跌、区间、成交量与基础市场状态。

## 对应代码
- `utils/binance_api.py` → `get_24h_ticker()` / `get_price()` / `get_all_prices()`
- `telegram_bot/main.py` → `/token <symbol>`
- `api_server/main.py` → `/api/ticker/<symbol>`

## 适用场景
- 查 BTC / ETH / SOL 当前价格
- 看 24h 高低点和成交额
- 为后续深度分析先拿基础行情

## 输入
- `symbol`：如 `BTCUSDT` / `ETHUSDT`

## 输出
- 最新价格
- 24h 涨跌幅
- 24h 高 / 低
- 24h 成交量 / 成交额
- 基础说明

## 推荐扩展
当用户继续追问时：
- 想看技术面 → `Trading Signal`
- 想看安全性 → `Token Audit`
- 想看是否在热点轮动 → `Meme Rush`

## 风险提示
- 这里只回答“是什么”，不直接等于交易建议
