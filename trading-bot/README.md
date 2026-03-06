# Binance Trading Bot

A simple RSI-based trading bot for Binance.

## Setup

```bash
pip install -r requirements.txt
```

Set environment variables:
```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_SECRET_KEY="your_secret_key"
```

## Usage

```bash
python main.py
```

## Strategy

- **Buy**: RSI < 30 (oversold)
- **Sell**: RSI > 70 (overbought)

## Disclaimer

Use at your own risk. This is for educational purposes.
