# Signal Alerts

Price alert system with Telegram notifications.

## Setup

```bash
pip install -r requirements.txt
```

Set environment variables:
```bash
export ALERT_SYMBOL="BTCUSDT"
export PRICE_ABOVE="75000"
export PRICE_BELOW="60000"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
```

## Usage

```bash
python main.py
```

Monitors price and sends Telegram alerts when threshold is crossed.
