# Video Recording Checklist

## Before Recording

- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Demo mode enabled: `DEMO_MODE=true` in `.env`
- [ ] LLM API key set (OpenAI or Anthropic)
- [ ] Redis running (optional but recommended)

## Recording Steps

1. **Start Backend** (Terminal 1):
   ```bash
   ./start_demo.sh
   ```
   Wait for: "Uvicorn running on http://0.0.0.0:8000"

2. **Run Demo** (Terminal 2):
   ```bash
   ./run_demo.sh
   ```

3. **Show Swagger UI**:
   - Open: http://localhost:8000/docs
   - Try the `/api/agent/message` endpoint interactively

## What to Say/Show

1. "This is an AI trading agent that processes natural language intents"
2. "Notice how different phrasings of the same intent produce consistent results"
3. "All operations complete in under 10 seconds"
4. "This is running in demo mode - no real money is used"
5. "The system is fully autonomous - no follow-up questions needed"

## Key Demonstrations

- Intent consistency (3+ phrasings)
- Order execution (mock)
- Latency metrics
- Multi-user support
- Swagger UI interaction

