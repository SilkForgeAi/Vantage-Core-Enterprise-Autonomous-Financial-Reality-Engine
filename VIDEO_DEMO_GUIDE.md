# Video Demo Guide

## Quick Start for Recording

### Terminal 1: Start Backend

```bash
./start_demo.sh
```

This will:
- Start Redis (if available)
- Start the FastAPI backend on port 8000
- Show API docs URL

### Terminal 2: Run Demo Script

```bash
./run_demo.sh
```

This will run 5 demo scenarios:
1. Health check
2. Balance check intent
3. Buy order intent
4. Intent consistency (3 different phrasings)
5. Position check

## What to Show in Video

### 1. Swagger UI (Interactive)
Open: http://localhost:8000/docs

Show:
- All available endpoints
- Try the `/api/agent/message` endpoint
- Show request/response format

### 2. Intent Consistency
Run the demo script and show:
- Same intent ("buy 0.1 BTC") with different phrasings
- All produce similar structured outputs
- Latency metrics (<10s)

### 3. Full Flow
Show a complete order execution:
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.1 BTC"}'
```

Show:
- Intent extraction
- LLM reasoning
- Order execution (mock)
- Fill confirmation
- Audit log

### 4. Multi-User
Show different users:
```bash
# User 1
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "message": "check balance"}'

# User 2 (simultaneously)
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user2", "message": "check balance"}'
```

## Key Points to Highlight

1. **Zero Hard-Coded Paths**: Show that same intent with different phrasings works
2. **Autonomous**: No follow-up questions needed
3. **Deterministic**: Same intent → same outcome
4. **Fast**: All requests <10s
5. **Safe**: Demo mode - no real money

## Demo Script Output

The `run_demo.sh` script will show:
- Health check response
- Intent processing results
- Latency metrics
- Execution IDs
- Success/failure status

All formatted nicely for screen recording.

