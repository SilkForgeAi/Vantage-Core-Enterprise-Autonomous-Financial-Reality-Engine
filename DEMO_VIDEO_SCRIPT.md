# Demo Video Script - AI Trading Agent

## Overview
This script guides you through creating a compelling demo video showcasing the AI Trading Agent's capabilities.

## Pre-Recording Setup

1. **Start Services:**
```bash
# Terminal 1: Start Redis
brew services start redis

# Terminal 2: Start Backend
cd /Users/brixxbeat/Desktop/AiAGENT
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 3: Keep open for API calls
```

2. **Verify Everything Works:**
```bash
curl http://localhost:8000/
# Should return: {"status": "running", ...}
```

## Video Structure (5-7 minutes)

### Part 1: Introduction (30 seconds)
- Show the project structure
- Mention: "AI Trading Agent that maps natural language to deterministic trading actions"
- Key features: Zero hard-coded paths, fully autonomous, deterministic execution

### Part 2: API Documentation (30 seconds)
- Open browser to http://localhost:8000/docs
- Show the Swagger UI
- Highlight endpoints:
  - `/api/agent/message` - Main entry point
  - `/api/user/add_exchange` - Add exchanges
  - `/api/user/{user_id}/status` - Check status

### Part 3: Natural Language Processing (2 minutes)
**Show Intent Extraction & Determinism**

Open terminal and run these commands one by one:

```bash
# Same intent, different phrasings - all produce identical results
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.1 BTC"}'

curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "I want to purchase 0.1 Bitcoin"}'

curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "Purchase 0.1 BTC please"}'
```

**Highlight:**
- All three produce the same normalized intent
- Symbol normalization (BTC, Bitcoin, BTCUSDT → BTC/USDT:USDT)
- Deterministic execution

### Part 4: Core Features Demo (3 minutes)

#### 4a. Balance Check (30 seconds)
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "check my USDT balance"}'
```

**Show:**
- Unified balance across multiple exchanges
- Real-time state from Redis
- Natural language understanding

#### 4b. Price Check (30 seconds)
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "what is the current price of Ethereum?"}'
```

**Show:**
- Symbol normalization (Ethereum → ETH/USDT:USDT)
- Real-time price fetching
- LLM-driven tool selection

#### 4c. Buy Order (45 seconds)
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.05 ETH"}'
```

**Show:**
- Intent extraction (buy, 0.05, ETH)
- Symbol normalization
- Exchange selection (based on balance availability)
- Order execution (in demo mode - simulated)
- Response with execution details

#### 4d. Position Check (30 seconds)
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "what positions do I have?"}'
```

**Show:**
- Unified position view across exchanges
- Autonomous decision-making (no follow-up questions)

#### 4e. Sell Order (30 seconds)
```bash
curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "sell 0.01 BTC"}'
```

**Show:**
- Complete trade lifecycle
- Execution confirmation

### Part 5: Architecture Highlights (1 minute)

**Show in code editor:**
1. **LangGraph Orchestration** (`agents/trading_agent.py`)
   - Stateful agent loop
   - Intent extraction → Reasoning → Execution → Audit

2. **Unified State Management** (`storage/state_manager.py`)
   - Cross-venue state in Redis
   - Per-user isolation

3. **Symbol Normalization** (`agents/symbol_normalizer.py`)
   - Handles variations, typos, fuzzy matching
   - Ensures deterministic mapping

4. **Demo Mode** (`exchanges/mock_exchange.py`)
   - Safe testing without real money
   - Full feature parity

### Part 6: Key Differentiators (30 seconds)

**Mention:**
- Zero hard-coded decision paths
- Fully autonomous (no follow-up questions)
- Deterministic (same intent → same outcome)
- Multi-exchange support
- Sub-10 second latency
- Atomic audit logging

### Part 7: Closing (30 seconds)
- Show GitHub repository
- Mention: Production-ready, meets all bounty requirements
- Call to action: Try it yourself

## Quick Demo Commands (Copy-Paste Ready)

Save this as `demo_commands.sh`:

```bash
#!/bin/bash
BASE="http://localhost:8000/api/agent/message"
USER="demo_user_1"

echo "=== Demo Commands ==="

echo -e "\n1. Check Balance:"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"check my USDT balance\"}" | python3 -m json.tool

echo -e "\n2. Get Price:"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what is the price of Bitcoin?\"}" | python3 -m json.tool

echo -e "\n3. Buy Order:"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"buy 0.05 ETH\"}" | python3 -m json.tool

echo -e "\n4. Check Positions:"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"what positions do I have?\"}" | python3 -m json.tool

echo -e "\n5. Sell Order:"
curl -s -X POST "$BASE" -H "Content-Type: application/json" \
  -d "{\"user_id\": \"$USER\", \"message\": \"sell 0.01 BTC\"}" | python3 -m json.tool
```

## Recording Tips

1. **Screen Recording:**
   - Use QuickTime (Mac) or OBS Studio
   - Record at 1080p minimum
   - Show terminal, browser, and code editor

2. **Terminal Setup:**
   - Use larger font (14-16pt)
   - Dark theme for better visibility
   - Clear terminal between commands (`clear`)

3. **Browser Setup:**
   - Swagger UI at http://localhost:8000/docs
   - Zoom to 125% for readability

4. **Code Editor:**
   - Use syntax highlighting
   - Show key files mentioned above
   - Keep it brief (don't read entire files)

5. **Pacing:**
   - Don't rush - let responses load
   - Pause to explain key concepts
   - Show the actual JSON responses

## What to Emphasize

1. **Autonomy:** Agent never asks follow-up questions
2. **Determinism:** Same intent = same outcome
3. **Natural Language:** Works with any phrasing
4. **Production-Ready:** Meets all bounty requirements
5. **Safety:** Demo mode for testing

## Post-Production

- Add text overlays for key points
- Add transitions between sections
- Include timestamps in description
- Add music (optional, keep it subtle)

