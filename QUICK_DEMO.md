# Quick Demo Setup (No Real Trades)

## 3-Step Demo Setup

### Step 1: Enable Demo Mode

Edit `.env` and add:
```bash
DEMO_MODE=true
ENABLE_LIVE_TRADING=false
```

### Step 2: Setup Demo User

```bash
python scripts/setup_demo_mode.py
```

This creates a demo user with mock exchanges (no API keys needed).

### Step 3: Start & Demo

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start backend
uvicorn backend.main:app --reload

# Terminal 3: Run demo
python demo_quick.py
```

## What You Get

- Full intent-to-execution flow
- Mock order execution (no real money)
- Balance updates (simulated)
- Fill confirmations
- Audit logs
- Latency metrics

## Test It

```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo_user_1",
    "message": "buy 0.1 BTC"
  }'
```

**Result**: Order executes in mock mode - you'll see fill confirmation, balance updates, but NO real money is used!

## Safety

- ✅ No real exchange connections
- ✅ No API keys required
- ✅ No real money at risk
- ✅ Perfect for demos and testing

