# Skill: Alpha Market Data

## 目标
围绕 Binance Alpha 场景提供代币列表、基础交易信息、K 线图与 24h 统计，帮助用户快速发现并跟踪新热点。

## 对应代码
- `utils/binance_api.py` → `get_binance_alpha_tokens()` / `get_24h_ticker()` / `get_klines()`
- `web_ui/main.py` → Dashboard / 图表 / 热门榜
- `api_server/main.py` → `GET /api/ticker/<symbol>` / `GET /api/top`
- `telegram_bot/main.py` → `/token` / `/top`

## 适用场景
- Alpha 列表里最近有哪些值得看的币？
- 某个 Alpha 代币的 24h 统计怎么样？
- 给我看这个币的 K 线和成交热度

## 输入
- `symbol`：如 `BTCUSDT` / `DEEPUSDT`
- `interval`：如 `15m` / `1h` / `4h` / `1d`
- `limit`：返回的榜单或 K 线数量

## 输出
- Alpha 候选代币列表
- 最新价格
- 24h 涨跌幅 / 高低点 / 成交量 / 成交额
- K 线数据
- 适合继续分析的候选标的

## 推荐搭配
- 先用 `Alpha Market Data` 找币和看热度
- 再用 `Trading Signal` 看趋势和关键位
- 如果是高风险小币，再接 `Token Audit`

## 当前实现边界
当前仓库已经有现货行情、K 线、热门榜与 Alpha 候选样例能力，适合作为比赛版 Alpha 数据入口；如果后续要完全对齐 Binance 官方 Alpha 专区，可继续补充更细的标签、筛选器和榜单维度。

## 风险提示
- Alpha 标的往往波动更大，热度不等于可交易性
- 24h 数据只适合做发现，不适合单独作为下单依据
