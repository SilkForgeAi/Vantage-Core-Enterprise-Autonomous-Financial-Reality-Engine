# REST API Demo Guide

## Safe Demo Mode (No Real Trades)

**IMPORTANT**: For demonstrations, use demo mode to avoid real trades:

```bash
# Enable demo mode in .env
DEMO_MODE=true

# Setup demo user with mock exchanges
python scripts/setup_demo_mode.py

# Then start backend and demo
uvicorn backend.main:app --reload
python demo_quick.py
```

See `DEMO_SAFE.md` for complete demo mode instructions.

## Quick Start

### 1. Start the Backend

```bash
# Make sure Redis is running
redis-server

# In a separate terminal, start the FastAPI backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

### 2. API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Demo Endpoints

### Health Check

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "status": "running",
  "service": "AI Trading Agent",
  "version": "1.0.0"
}
```

### Add Exchange for User

First, encrypt your API keys:

```bash
python scripts/add_user_exchange.py test_user_1 binance YOUR_API_KEY YOUR_API_SECRET
```

Or use the API directly (requires encrypted keys):

```bash
curl -X POST "http://localhost:8000/api/user/add_exchange" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "exchange_name": "binance",
    "encrypted_api_key": "encrypted_key_here",
    "encrypted_api_secret": "encrypted_secret_here"
  }'
```

### Process Message (Main Demo)

This is the core functionality - natural language to execution:

```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "check my USDT balance"
  }'
```

Response:
```json
{
  "execution_id": "exec_1234567890",
  "response": "Your USDT balance across all exchanges is...",
  "action_taken": "get_balance(asset='USDT') -> {...}",
  "latency_ms": 2345.6,
  "success": true
}
```

### More Intent Examples

Buy order:
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "buy 0.1 BTC"
  }'
```

Check positions:
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_1",
    "message": "what positions do I have?"
  }'
```

### Get User Status

```bash
curl http://localhost:8000/api/user/test_user_1/status
```

### Get Unified Balances

```bash
curl http://localhost:8000/api/user/test_user_1/balances
```

### Get Unified Positions

```bash
curl http://localhost:8000/api/user/test_user_1/positions
```

## Demo Script

Run the automated demo:

```bash
chmod +x demo_api.sh
./demo_api.sh
```

## Key Demo Points

1. Intent Consistency: Try 50+ phrasings of the same intent
   - "buy 0.1 BTC"
   - "I want to buy 0.1 Bitcoin"
   - "Purchase 0.1 BTC please"
   All should produce identical outcomes

2. Autonomous Execution: No follow-up questions
   - Agent resolves intent with available context
   - Returns deterministic action

3. Latency: All requests complete in <10 seconds
   - Check `latency_ms` in response

4. Multi-User: Test with different user_ids
   - Each user has isolated state

## Testing Intent Variations

```bash
# Test 1
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "message": "buy 0.1 BTC"}'

# Test 2 (different phrasing, same intent)
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "message": "I want to purchase 0.1 Bitcoin"}'

# Both should produce identical normalized intents
```

## Video Demo Tips

1. Show Swagger UI at /docs for interactive testing
2. Demonstrate intent consistency with multiple phrasings
3. Show latency metrics in responses
4. Test with multiple users simultaneously
5. Show audit logs in ./audit_logs/

