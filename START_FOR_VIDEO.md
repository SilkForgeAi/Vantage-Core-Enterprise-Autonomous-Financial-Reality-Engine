# Start Demo for Video Recording

## Step-by-Step Instructions

### Terminal 1: Start Backend

```bash
cd /Users/brixxbeat/Desktop/AiAGENT

# Make sure dependencies are installed
pip3 install fastapi uvicorn pydantic pydantic-settings langchain langchain-openai langchain-anthropic langchain-core langgraph structlog redis chromadb cryptography httpx python-dotenv ccxt

# Start the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Wait until you see: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Run Demo

```bash
cd /Users/brixxbeat/Desktop/AiAGENT
./run_demo.sh
```

### Terminal 3 (Optional): Show Swagger UI

Open in browser: http://localhost:8000/docs

## What the Demo Shows

1. Health check endpoint
2. Intent processing (balance check)
3. Order execution (buy 0.1 BTC)
4. Intent consistency (3 different phrasings)
5. Position checking

All in DEMO MODE - no real money used!

## Quick Test Commands

```bash
# Test 1: Health
curl http://localhost:8000/

# Test 2: Process message
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "check my USDT balance"}'

# Test 3: Buy order
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.1 BTC"}'
```

## For Video

1. Start backend in Terminal 1
2. Show Swagger UI (http://localhost:8000/docs)
3. Run demo script in Terminal 2
4. Highlight:
   - Intent consistency
   - Latency (<10s)
   - Autonomous execution
   - Demo mode safety

