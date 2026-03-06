# Crypto Educator

AI-powered crypto education assistant using OpenAI + Binance API.

## Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_openai_key"
export BINANCE_API_KEY="your_binance_key"  # optional
```

## Usage

```bash
python main.py
```

## Features

- **Chat**: Ask any crypto question
- `/price <symbol>` - Get price info (e.g., /price BTCUSDT)
- `/top` - Top coins by trading volume
- Real-time Binance market data

## Example Questions

- "What is RSI and how does it work?"
- "Explain Binance Futures"
- "What's the difference between spot and margin trading?"
