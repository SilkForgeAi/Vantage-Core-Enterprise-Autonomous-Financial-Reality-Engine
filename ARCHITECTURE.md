Architecture Documentation

System Overview

This AI Trading Agent implements a closed-loop system that maps natural language intents directly to deterministic trading actions on live exchanges. The architecture is designed to meet the strict requirements of the $30K ProbeAGI bounty challenge.

Core Principles

1. Zero Hard-Coded Paths: All decision-making is LLM-driven. No if-else chains or predefined logic trees.
2. Intent Consistency: 50+ natural language variations of the same intent must produce identical outcomes.
3. Unified State: Cross-venue synchronized balances and positions provide "proprioception" to the agent.
4. Autonomous Execution: Zero follow-up questions - agent takes full responsibility for decisions.
5. Sub-10s Latency: End-to-end from message to fill confirmation in <10 seconds.
6. Atomic Auditing: Every execution emits structured logs with full reasoning chains.

Component Architecture

1. Agent Layer (agents/)

TradingAgent (agents/trading_agent.py)
- LangGraph-based stateful agent
- Dynamic intent extraction via LLM
- Tool-based execution model
- Memory integration for context

Key Flow:

Tools (agents/tools.py):
- get_balance: Unified balance query across exchanges
- get_position: Position details across venues
- place_order: Execute trades (real money)
- get_ticker: Current price information

2. Exchange Layer (exchanges/)

ExchangeManager (exchanges/exchange_manager.py)
- Manages multiple exchange connections per user
- Unified interface across exchanges
- Per-user isolation

CCXTExchange (exchanges/ccxt_exchange.py)
- CCXT-based implementation
- Supports any CCXT-compatible exchange
- WebSocket/polling for real-time updates

BaseExchange (exchanges/base_exchange.py)
- Abstract interface for exchange implementations
- Unified data structures (Balance, Position, OrderFill)

3. State Management (storage/)

UnifiedStateManager (storage/state_manager.py)
- Redis-backed state storage
- Per-user namespacing
- Unified cross-venue views
- Real-time synchronization

UserMemoryManager (storage/memory_manager.py)
- ChromaDB vector memory
- Persistent conversation history
- Intent-outcome mappings
- Semantic search for relevant context

4. Security (security/)

KeyEncryption (security/encryption.py)
- Fernet encryption for API keys
- PBKDF2 key derivation
- Per-user key isolation
- Secure storage at rest

5. Audit System (audit/)

AuditLogger (audit/audit_logger.py)
- Atomic log writes (JSON files)
- Structured execution logs
- Reasoning chain preservation
- State snapshots at execution time

6. Backend (backend/)

FastAPI Server (backend/main.py)
- REST API for multi-user access
- Endpoints for message processing
- Exchange management
- State queries

State Sync Service (backend/state_sync.py)
- Background task for state synchronization
- Periodic updates from exchanges to Redis
- Maintains unified state views

Telegram Bot (backend/telegram_bot.py)
- Natural language interface
- Routes messages to agent
- Real-time responses

Data Flow

Message Processing Flow

State Synchronization Flow

Multi-User Isolation

Each user has:
- Isolated Exchange Connections: Separate CCXTExchange instances
- Separate State Namespace: Redis keys prefixed with user:{user_id}:
- Independent Memory: ChromaDB collection per user
- Separate Agent Instance: TradingAgent per user
- Independent Audit Logs: Logs keyed by user_id

Intent-to-Execution Mapping

The Core Challenge

The system must ensure that 50+ phrasings like:
- "buy 0.1 BTC"
- "I want to buy 0.1 Bitcoin"
- "Purchase 0.1 BTC please"
- etc.

All produce identical deterministic actions.

Solution

1. Structured Intent Extraction: LLM extracts intent to JSON format
2. Consistent Parsing: Same intent structure regardless of phrasing
3. Unified State Context: Same state → same decision
4. No Hard-Coded Rules: LLM makes decisions based on context, not if-else logic

Testing

tests/test_intent_consistency.py validates this with 50+ phrasings per intent type.

Performance Optimization

Latency Targets

- Intent Extraction: <2s
- State Fetch: <500ms (Redis)
- LLM Reasoning: <5s
- Order Execution: <2s (exchange-dependent)
- Total: <10s (strict requirement)

Optimization Strategies

1. Redis Caching: Unified state cached in Redis (5min TTL)
2. Async Operations: All I/O is async
3. Parallel Tool Calls: When possible, tools execute in parallel
4. State Sync: Background sync keeps Redis warm
5. Memory Search: Limit to top-N relevant results

Security Considerations

1. API Key Encryption: Fernet encryption at rest
2. Per-User Isolation: No cross-user data leakage
3. Secure Storage: Keys never logged or exposed
4. Audit Trails: Full logging for compliance
5. Rate Limiting: (To be implemented in production)

Deployment Architecture

Development

Production (Recommended)

Extension Points

Adding New Exchanges

1. Exchange must support CCXT
2. Add to ExchangeManager.add_exchange()
3. No code changes needed in agent layer

Adding New Tools

1. Create tool in agents/tools.py
2. Add to create_tools() return list
3. Agent automatically gets access via tool calling

Customizing Agent Behavior

1. Modify system prompts in TradingAgent._reason_and_execute()
2. Adjust temperature in LLM initialization
3. Change memory search parameters

Known Limitations & Future Improvements

1. WebSocket Implementation: Currently uses polling fallback for some exchanges
   - Fix: Use exchange-specific WebSocket libraries (python-binance, pybit)

2. Order Routing: Currently uses first available exchange
   - Fix: Implement smart routing based on liquidity, fees, balances

3. Error Recovery: Limited retry logic
   - Fix: Add exponential backoff, circuit breakers

4. Rate Limiting: Not implemented
   - Fix: Add per-user rate limits to prevent abuse

5. Structured Output: Intent parsing uses JSON extraction
   - Fix: Use LLM structured output APIs when available

6. Multi-Exchange Orders: Can't split orders across exchanges
   - Fix: Add order splitting logic for large orders

Testing Strategy

1. Unit Tests: Individual components
2. Integration Tests: End-to-end flows
3. Consistency Tests: Intent variations (50+ per intent)
4. Latency Tests: Performance validation
5. Load Tests: Multi-user concurrent execution

Monitoring & Observability

- Structured Logging: structlog with JSON output
- Audit Logs: Execution traces with reasoning
- Latency Tracking: Per-execution latency logging
- Error Tracking: Exception logging with context

Compliance & Audit

Every execution produces:
- Unique execution_id
- Timestamp
- User ID
- Intent (extracted)
- Reasoning chain (LLM output)
- Action taken
- Unified state snapshot (at execution time)
- Latency metrics
- Error details (if any)

All logs are atomic (single JSON file per execution) and traceable.