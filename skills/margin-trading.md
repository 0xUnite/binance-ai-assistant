# Skill: Margin Trading

## 目标
围绕全仓与逐仓杠杆交易整理借还款、杠杆下单、逐仓账户管理、利率与抵押率查询、杠杆倍数调整、强平记录与小额负债兑换等能力设计。

## 对应代码
- `utils/user_guardrails.py` → 保证金占用、风险预算、仓位约束
- `utils/trading_advisor.py` → 交易计划与仓位建议
- `portfolio-tracker/main.py` → 资产视图与持仓汇总
- `ai_assistant/main.py` → 账户与资产问答入口
- `utils/binance_api.py` → 现有账户/下单封装，可继续向 margin API 延展

## 适用场景
- 评估某笔杠杆交易需要多少保证金
- 判断更适合全仓还是逐仓
- 在接入真实杠杆接口前，先生成安全的借贷与交易建议

## 输入
- `symbol`
- `side`：BUY / SELL
- `mode`：cross / isolated
- `leverage`
- `entry_price` / `stop_loss`
- 可选：风险预算、账户规模

## 输出
- 保证金需求
- 建议杠杆与仓位大小
- 逐仓 / 全仓模式说明
- 借贷与执行前检查项
- 风险预警：强平距离、杠杆是否过高、是否超预算

## 推荐搭配
- 用 `Token Info` / `Trading Signal` 判断值不值得做
- 用 `Margin Trading` 计算怎么做更安全
- 用日志和复盘模块追踪杠杆策略的结果

## 当前实现边界
当前仓库更强的是“风险预算 + 仓位建议 + 账户视图”，还不是完整的 Binance 杠杆 API 客户端；因此比赛文档里应把它表述为“已具备杠杆交易工作流骨架，可继续接入借还款、OCO/OTO/OTOCO 和逐仓账户操作接口”。

## 风险提示
- 杠杆不是收益加速器，更多时候是爆仓加速器
- 全仓模式尤其要谨慎，别让一笔错误把整个账户拖下水
