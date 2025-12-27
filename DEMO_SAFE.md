# Safe Demo Mode - No Real Trades

## Three Ways to Demo Safely

### Option 1: Demo Mode (Recommended - No Exchange API Keys Needed)

This uses mock exchanges that simulate real behavior without any API connections.

1. Enable demo mode in `.env`:
```bash
DEMO_MODE=true
ENABLE_LIVE_TRADING=false
```

2. Set up demo user:
```bash
python scripts/setup_demo_mode.py
```

3. Start backend:
```bash
uvicorn backend.main:app --reload
```

4. Test the API:
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "buy 0.1 BTC"
  }'
```

**Result**: Order executes in mock mode - updates mock balances, returns fill confirmation, but NO real money is used.

### Option 2: Sandbox/Testnet Mode (Requires Exchange Testnet API Keys)

Use real exchange testnet/sandbox environments.

1. Get testnet API keys from exchanges:
   - Binance Testnet: https://testnet.binancefuture.com/
   - Bybit Testnet: https://testnet.bybit.com/

2. Keep in `.env`:
```bash
ENABLE_LIVE_TRADING=false  # This enables sandbox mode
DEMO_MODE=false
```

3. Add exchanges with testnet keys:
```bash
python scripts/add_user_exchange.py demo_user_1 binance TESTNET_KEY TESTNET_SECRET
```

**Result**: Connects to real testnet, uses testnet funds (free), but no real money.

### Option 3: No Exchanges (Intent Processing Only)

Test intent extraction and reasoning without any exchange connection.

1. Just start the backend (no exchanges needed):
```bash
uvicorn backend.main:app --reload
```

2. Test intent processing:
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "check my USDT balance"
  }'
```

**Result**: Agent processes intent, extracts structured output, but returns error about no exchanges (which is fine for demo).

## Recommended Demo Flow

For the bounty demo, use **Option 1 (Demo Mode)**:

```bash
# 1. Enable demo mode
echo "DEMO_MODE=true" >> .env

# 2. Setup demo user with mock exchanges
python scripts/setup_demo_mode.py

# 3. Start backend
uvicorn backend.main:app --reload

# 4. Run demo
python demo_quick.py
```

## What Demo Mode Shows

✅ Full intent-to-execution flow
✅ Deterministic symbol normalization
✅ LLM-driven decision making
✅ Order execution simulation
✅ Balance updates (mock)
✅ Fill confirmations
✅ Audit logging
✅ Latency metrics
✅ Multi-user support

❌ NO real money used
❌ NO real exchange connections
❌ NO API keys required

## Demo Scripts

- `demo_quick.py` - Python demo script
- `demo_api.sh` - Shell script demo
- `scripts/setup_demo_mode.py` - Setup demo user

## Safety Checklist

Before demo:
- [ ] `DEMO_MODE=true` in `.env`
- [ ] `ENABLE_LIVE_TRADING=false` in `.env`
- [ ] No real API keys in `.env` (or use testnet keys)
- [ ] Run `setup_demo_mode.py` to create demo user
- [ ] Test with `demo_quick.py` first

During demo:
- Show Swagger UI at `/docs`
- Demonstrate intent consistency
- Show mock order execution
- Display latency metrics
- Show audit logs

After demo:
- All trades were simulated
- No real money was used
- System is ready for real use when needed

