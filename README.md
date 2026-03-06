# Binance AI Assistant 🤖

功能强大的 Binance 智能交易助手

## 🆕 v4.2 - 参赛最终版

基于 OpenClaw AI Framework 构建，提供全方位的 Binance 交易支持。

## ✨ 核心功能

### 🌐 Web 仪表盘
- ✅ 实时价格展示
- ✅ K线图表 (Chart.js)
- ✅ 技术信号显示
- ✅ 热门代币排行
- ✅ 响应式设计

### 🤖 Telegram Bot
- `/start` - 启动菜单
- `/portfolio` - 查看仓位
- `/analyze BTC` - 市场分析
- `/trade SOL` - 交易计划
- `/top` - 热门代币
- 自然语言对话支持

### 📊 市场数据
- ✅ 实时价格查询
- ✅ 24小时行情数据
- ✅ K线数据 (多时间周期)
- ✅ 订单簿深度
- ✅ 资金费率查询
- ✅ 热门代币排行

### 📈 技术分析
- ✅ RSI 指标
- ✅ MACD 指标
- ✅ MA 移动平均线
- ✅ 布林带
- ✅ 市场趋势判断
- ✅ 交易信号生成

### 🐋 巨鲸追踪
- ✅ Open Interest 持仓分析
- ✅ 大额转账监控
- ✅ 流动性区域 (清算集群)
- ✅ 多空比分析
- ✅ 资金费率情绪

### 🔗 多链热点扫描
- ✅ Solana 热点代币
- ✅ BSC 热点代币
- ✅ Base 热点代币
- ✅ 实时行情监控

### 🔐 代币安全审计
- ✅ Honeypot 检测
- ✅ 合约安全分析
- ✅ 流动性检查
- ✅ 黑名单检测

### 💰 仓位管理
- ✅ 实时盈亏追踪
- ✅ 止损止盈设置
- ✅ 历史交易记录
- ✅ 胜率统计

### 🎯 交易计划生成
- ✅ 入场区间推荐
- ✅ 止损位设置
- ✅ DCA 补仓位
- ✅ 目标盈利位
- ✅ 建议杠杆

### 📝 AI Post 生成器
- ✅ 一键生成市场分析推文
- ✅ 支持 Twitter 推文串
- ✅ 包含实时数据 + 技术指标

### 🔬 策略回测
- ✅ RSI 策略回测
- ✅ MA 交叉策略回测
- ✅ MACD 策略回测
- ✅ 收益率统计
- ✅ 最大回撤计算

### 🎮 模拟交易
- ✅ 虚拟买入/卖出
- ✅ 盈亏实时计算
- ✅ 交易历史记录

## 🚀 快速开始

```bash
git clone https://github.com/0xUnite/binance-ai-assistant.git
cd binance-ai-assistant
pip install -r requirements.txt

# 启动 Web 仪表盘
python web_ui/main.py

# 启动 Telegram Bot
python telegram_bot/main.py

# 策略回测
python backtest/main.py BTCUSDT
```

## 📁 项目结构

```
binance-ai-assistant/
├── telegram_bot/          # 🤖 Telegram Bot
├── ai_assistant/         # 🤖 AI 智能助手
├── api_server/           # 🌐 REST API
├── web_ui/               # 🌐 Web 仪表盘
├── post_generator/       # 📝 AI Post 生成器
├── backtest/             # 🔬 策略回测
├── trading-bot/          # 📈 交易机器人
├── indicators/           # 📊 技术指标库
└── utils/               # 🔧 工具函数
```

## 🤝 参赛亮点

✅ **完整产品矩阵** - Web + Telegram + CLI
✅ **专业技术分析** - RSI/MACD/MA/BB
✅ **巨鲸活动追踪** - OI + 清算 + 大额交易
✅ **多链热点** - SOL/BSC/Base 实时监控
✅ **代币安全** - Honeypot 检测
✅ **策略回测** - 3种策略对比
✅ **AI 生成** - 一键 Post 生成
✅ **模拟交易** - 零风险测试

## ⚠️ 风险提示

- 本项目所有交易建议仅供参考
- 不构成投资建议
- 投资有风险，入市需谨慎
