# Quick Start Guide

Get the AI Trading Agent running in 5 minutes.

1. Install Dependencies

```bash
pip install -r requirements.txt
```

2. Generate Configuration

```bash
python setup.py
```

This creates a `.env` file with auto-generated encryption key.

3. Configure API Keys

Edit `.env` and add:

```bash
# Required: At least one LLM API key
ANTHROPIC_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here

# Optional: Telegram bot (for Telegram interface)
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Optional: Exchange API keys (for live trading)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
```

4. Start Redis

```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Or run directly
redis-server
```

5. Start Backend

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

6. (Optional) Start Telegram Bot

In a new terminal:

```bash
python backend/telegram_bot.py
```

7. Test It

Via API

```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "check my USDT balance"
  }'
```

Via Telegram

1. Find your bot on Telegram
2. Send `/start`
3. Send: `check my USDT balance`

Adding Exchanges

Before you can trade, add exchanges for a user:

```bash
python scripts/add_user_exchange.py test_user_1 binance <api_key> <api_secret>
```

Or use the API directly (requires encrypting keys first - see `scripts/add_user_exchange.py` for reference).

Important Safety Notes

⚠️ By default, trading is DISABLED (`ENABLE_LIVE_TRADING=false` in `.env`)

The system will:
- ✅ Connect to exchanges
- ✅ Fetch balances and positions
- ✅ Process intents
- ❌ NOT place real orders

To enable live trading:
1. Set `ENABLE_LIVE_TRADING=true` in `.env`
2. Test thoroughly first with small amounts
3. Start with testnet/sandbox if available

Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- Run tests: `pytest tests/test_intent_consistency.py -v`
- Review audit logs in `./audit_logs/`

