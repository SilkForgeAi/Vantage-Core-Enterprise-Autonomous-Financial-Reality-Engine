# AI Trading Agent - $30K Bounty Challenge

A production-ready AI trading agent system designed to close the "Context Gap" between natural language intents and deterministic execution on live exchanges.

Core Architecture Principles

1. Dynamic Intent-to-Execution: Zero hard-coded paths - all decisions are LLM-driven
2. Multi-User Isolation: 5+ concurrent users with independent control loops
3. Live Exchange Integration: Real capital on 2+ exchanges (Binance, Bybit, etc.)
4. Sub-10s Latency: End-to-end from message to fill confirmation
5. Autonomous Execution: Zero follow-up questions, full agent responsibility
6. Unified State: Cross-venue synchronized balances and risk profiles
7. Atomic Auditing: Structured post-trade logs with reasoning chains

Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys, LLM keys, Redis connection, etc.

# Initialize Redis (required)
redis-server

# Run the backend
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Run Telegram bot (in separate terminal)
python backend/telegram_bot.py
```

Project Structure

```
.
├── backend/           # FastAPI backend and core services
├── agents/            # LangGraph agent orchestration
├── exchanges/         # CCXT exchange integrations
├── storage/           # Redis, ChromaDB, and state management
├── security/          # API key encryption and auth
├── audit/             # Post-trade logging and audit trails
├── tests/             # Testing framework for intent consistency
└── config/            # Configuration files
```

Key Features

- LangGraph Agent: Stateful agent with memory and tool calling
- CCXT Integration: Multi-exchange support (Binance, Bybit, any CCXT exchange)
- Redis State: Per-user isolated state with unified cross-venue views
- ChromaDB Memory: Persistent vector memory per user
- Telegram Interface: Natural language trading interface
- Audit System: Atomic logs with reasoning chains
- Dynamic Intent Mapping: Zero hard-coded paths - all LLM-driven
- Intent Consistency Testing: Validates 50+ phrasings produce identical outcomes

Documentation

- [Setup Guide](SETUP.md) - Installation and configuration instructions
- [Architecture](ARCHITECTURE.md) - System design, data flows, and component details

Testing Intent Consistency

Run the consistency test suite to verify that 50+ phrasings of the same intent produce identical outcomes:

```bash
pytest tests/test_intent_consistency.py -v
```

Security

- API keys encrypted at rest using cryptography
- Per-user key isolation
- Secure Redis connections
- Environment-based secrets management

License

Built for the ProbeAGI $30K Bounty Challenge

