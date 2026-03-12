# Skill: Spot

## 目标
围绕 Binance 现货账户提供余额查询、持仓查看与下单相关能力。

## 对应代码
- `utils/binance_api.py` → `get_account_balance()` / `place_order()`
- `portfolio-tracker/main.py`
- `telegram_bot/main.py` → `/balance` / `/portfolio` / `/connect`
- `api_server/main.py` → `/api/balance`

## 适用场景
- 看账户余额和资产分布
- 生成现货执行建议
- 小额试单或演示交易流程

## 输入
- 账户 API Key（环境变量或安全存储）
- 交易对、方向、数量、订单类型

## 输出
- 余额 / 持仓
- 订单执行结果
- 交易前后资产变化

## 强约束
- 默认只建议开启读取权限或最小必要交易权限
- **严禁开启提现权限**
- 任何自动化下单都应该二次确认

## 风险提示
- Spot 能力直接触及真实资产，必须把风控放在第一位
