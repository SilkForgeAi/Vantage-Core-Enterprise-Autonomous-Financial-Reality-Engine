# Demo Scenarios for Video

## Scenario 1: Intent Consistency (Critical Feature)
**Purpose:** Show that 50+ phrasings produce identical outcomes

**Commands:**
```bash
# All should produce the same normalized intent: buy 0.1 BTC
"buy 0.1 BTC"
"I want to buy 0.1 Bitcoin"
"Purchase 0.1 BTC please"
"Can you buy me 0.1 BTC?"
"I'd like to purchase 0.1 Bitcoin"
"Execute a buy order for 0.1 BTC"
```

**What to Show:**
- All extract the same intent: `{"intent": "buy", "symbol": "BTC/USDT:USDT", "amount": 0.1}`
- Same execution path
- Same outcome

## Scenario 2: Symbol Normalization
**Purpose:** Show robust symbol handling

**Commands:**
```bash
"buy 0.1 BTC"           → BTC/USDT:USDT
"buy 0.1 Bitcoin"        → BTC/USDT:USDT
"buy 0.1 BTCUSDT"         → BTC/USDT:USDT
"buy 0.1 BTC-PERP"        → BTC/USDT:USDT
"buy 0.1 btc"            → BTC/USDT:USDT (case insensitive)
```

**What to Show:**
- All variations normalize to the same symbol
- Handles typos and different formats

## Scenario 3: Autonomous Decision Making
**Purpose:** Show zero follow-up questions

**Commands:**
```bash
"buy 0.1 BTC"  # Agent should:
- Check balance automatically
- Select best exchange
- Execute order
- Return confirmation

# NOT ask:
- "Which exchange?"
- "What price?"
- "Confirm?"
```

**What to Show:**
- Single message → complete execution
- No back-and-forth
- Fully autonomous

## Scenario 4: Multi-Exchange Unified State
**Purpose:** Show cross-venue state management

**Setup:**
- User has balances on Binance and Bybit
- Show unified view

**Commands:**
```bash
"check my USDT balance"
# Shows: Total across all exchanges + breakdown by exchange

"what positions do I have?"
# Shows: All positions across all exchanges
```

**What to Show:**
- Unified balance: 20,000 USDT (10k Binance + 10k Bybit)
- Agent uses unified state for decisions
- Cross-venue awareness

## Scenario 5: Complete Trade Lifecycle
**Purpose:** Show end-to-end trading flow

**Sequence:**
1. Check balance
2. Get price
3. Place buy order
4. Check positions
5. Place sell order
6. Verify balance update

**What to Show:**
- Complete workflow
- State persistence
- Audit logging (mention, don't show logs)

## Scenario 6: Error Handling
**Purpose:** Show graceful error handling

**Commands:**
```bash
"buy 1000 BTC"  # Insufficient balance
# Should: Detect insufficient balance, return error, don't execute

"buy 0.1 INVALID"  # Invalid symbol
# Should: Try to normalize, if fails, return clear error
```

**What to Show:**
- Graceful error messages
- No crashes
- Clear feedback

## Scenario 7: Latency Demonstration
**Purpose:** Show sub-10 second execution

**Commands:**
```bash
# Time the response
time curl -X POST "http://localhost:8000/api/agent/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "demo_user_1", "message": "buy 0.1 BTC"}'
```

**What to Show:**
- Response time in JSON: `"latency_ms": 3500.0`
- Well under 10 seconds
- Fast enough for real trading

## Scenario 8: Swagger UI Interaction
**Purpose:** Show developer-friendly API

**Steps:**
1. Open http://localhost:8000/docs
2. Show available endpoints
3. Try a request in the UI
4. Show response

**What to Show:**
- Interactive API documentation
- Easy to test
- Production-ready API

## Recommended Video Flow

1. **Hook (0:00-0:15):** Quick demo of natural language → trade execution
2. **Problem (0:15-0:30):** Context gap, hard-coded paths, follow-up questions
3. **Solution (0:30-1:00):** Our approach - LLM-driven, autonomous, deterministic
4. **Features (1:00-4:00):** 
   - Intent consistency (Scenario 1)
   - Symbol normalization (Scenario 2)
   - Autonomous execution (Scenario 3)
   - Multi-exchange (Scenario 4)
   - Complete lifecycle (Scenario 5)
5. **Architecture (4:00-5:00):** Quick code walkthrough
6. **Closing (5:00-5:30):** Key differentiators, call to action

## Pro Tips

1. **Prepare Responses:** Run commands once before recording to ensure responses are ready
2. **Clear Terminal:** Use `clear` between sections
3. **Highlight JSON:** Use `python3 -m json.tool` for pretty output
4. **Show Latency:** Point out the `latency_ms` field in responses
5. **Emphasize Safety:** Mention demo mode multiple times
6. **Show Code:** Quick glimpses of key files (don't read entire files)

