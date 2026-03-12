# Skill: Meme Rush

## 目标
发现高波动、高讨论度、高轮动速度的小币 / meme 机会，并给出“是否值得继续看”的快速判断。

## 对应代码
- `utils/multi_chain_scanner.py`
- `utils/alpha_radar.py`
- `utils/social_trading.py`
- `web_ui/main.py` → Alpha / 多链 / 跟单页

## 适用场景
- 最近有哪些 meme 在跑？
- 哪条链最热？
- 有哪些 Smart Money / KOL 动向值得盯？

## 输入
- 链名称（Solana / BSC / Base 等）
- 风险偏好
- 是否偏向“超早期”或“已放量”标的

## 输出
- 候选标的列表
- 热度来源（成交量、讨论度、Smart Money、链上异动）
- 风险标签
- 后续动作建议：加入观察列表 / 先审计 / 只做情报跟踪

## 推荐搭配
- 先用 `Meme Rush` 找标的
- 再用 `Token Audit` 排雷
- 最后用 `Trading Signal` 看节奏

## 风险提示
- Meme 赛道波动极大，最容易赚钱，也最容易被狠狠干掉
- 没有风控就别碰
