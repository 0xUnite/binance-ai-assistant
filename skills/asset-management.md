# Skill: Asset Management

## 目标
围绕充值、提现、账户信息、现货与资金账户余额、充提历史、BNB 手续费抵扣与碎币转换，构建统一的资产管理视图。

## 对应代码
- `utils/binance_api.py` → `get_account_balance()` / 账户信息基础封装
- `portfolio-tracker/main.py` → 资产估值、持仓分布、组合总览
- `ai_assistant/main.py` → 余额查询与账户问答
- `telegram_bot/main.py` → `/balance` / `/portfolio`
- `api_server/main.py` → `GET /api/balance`

## 适用场景
- 看账户余额、主要持仓和 USDT 估值
- 做资产分布检查和账户快照
- 为后续充值/提现/碎币转换等管理动作提供统一入口

## 输入
- 账户 API Key（只读优先）
- 可选：账户维度（spot / funding / unified 视图）
- 可选：是否展示估值与持仓占比

## 输出
- 账户余额与资产列表
- 估值汇总与主要仓位
- 账户管理建议：集中度、闲置资产、手续费优化方向
- 扩展能力入口：充提历史 / BNB 抵扣 / 碎币转换

## 推荐搭配
- `Asset Management`：先看账户现状
- `Spot` / `USDⓈ-M Futures Trading`：再决定如何执行交易
- `Daily Review` / 日志模块：复盘资产变化和行为表现

## 当前实现边界
当前仓库已经具备余额查询、持仓估值与组合视图，适合作为资产管理 Skill 的基础层；若要完全对齐 Binance 官方资产管理能力，可继续接入充值地址、提现记录、资金账户、BNB 抵扣状态与小额资产转换接口。

## 强约束
- 默认只建议开启读取权限
- **不要为比赛演示或测试账号开启提现权限**
- 涉及真实资产流转的动作必须显式确认

## 风险提示
- 资产管理看起来不刺激，但一旦误操作，损失往往最直接
- 任何自动化资产操作都应有白名单、确认和审计日志
