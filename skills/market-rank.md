# Skill: Market Rank

## 目标
快速输出 Binance 市场热度榜单，帮助用户发现当前最活跃、最值得跟踪的交易对。

## 对应代码
- `utils/binance_api.py` → `get_top_coins()`
- `web_ui/main.py` → Dashboard 热门榜
- `telegram_bot/main.py` → `/top`
- `api_server/main.py` → `/api/top`

## 适用场景
- 今天市场最热的是谁？
- 哪些币成交量最高？
- 我想做一份 Daily Briefing 的开场摘要

## 输入
- `limit`：返回数量，默认 10
- 可选过滤：只看 USDT 对、只看涨幅前列、只看高成交量

## 输出
- 排名
- 交易对
- 最新价格
- 24h 涨跌幅
- 24h 成交额

## 建议回答模板
1. 先给前 5~10 名榜单
2. 再点出 1~3 个异常项（放量、剧烈波动、情绪反转）
3. 如果用户要进一步分析，交给 `Token Info` 或 `Trading Signal`

## 风险提示
- 成交量高不等于趋势一定持续
- 热门榜适合做发现，不适合单独作为下单依据
