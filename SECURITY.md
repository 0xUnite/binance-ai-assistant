# Security Notes

## 密钥管理

本项目通过环境变量读取以下敏感配置：

- `BINANCE_API_KEY`
- `BINANCE_SECRET_KEY`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## 已采取措施

- 仓库内仅保留 `.env.example` 占位符
- 新增 `.gitignore`，默认忽略 `.env`、虚拟环境、日志和 `__pycache__`
- README 示例不包含真实密钥

## 使用建议

1. 不要把真实密钥写进源码或提交到 Git
2. Binance API 不要开启提现权限
3. 最好为不同模块使用不同 API Key
4. 生产环境使用 Secret Manager / CI Secret

## 赛后建议

可增加：
- `python-dotenv` 统一加载 `.env`
- pre-commit secret scan
- GitHub Actions secret scanning / gitleaks
