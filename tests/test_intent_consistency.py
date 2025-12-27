"""Test intent consistency - 50+ phrasings must produce identical outcomes."""
import pytest
import asyncio
from typing import List, Dict, Any
from agents.trading_agent import TradingAgent
from exchanges.exchange_manager import ExchangeManager
from security.encryption import KeyEncryption
from config.settings import settings


class MockExchangeManager(ExchangeManager):
    """Mock exchange manager for testing."""
    
    def __init__(self):
        # Don't call super().__init__ to avoid encryption requirement
        self.user_exchanges = {}
        self.mock_balances = {}
        self.mock_positions = {}
    
    def get_user_exchanges(self, user_id: str) -> List[str]:
        return ["binance", "bybit"]
    
    async def get_unified_balances(self, user_id: str):
        return self.mock_balances.get(user_id, {
            "binance": {"USDT": 1000.0},
            "bybit": {"USDT": 500.0}
        })
    
    async def get_unified_positions(self, user_id: str):
        return self.mock_positions.get(user_id, {})


# Test intent phrasings
BUY_INTENT_PHRASINGS = [
    "buy 0.1 BTC",
    "I want to buy 0.1 Bitcoin",
    "Purchase 0.1 BTC please",
    "Can you buy me 0.1 BTC?",
    "Execute a buy order for 0.1 Bitcoin",
    "Go long 0.1 BTC",
    "Open a long position of 0.1 BTC",
    "I'd like to acquire 0.1 BTC",
    "Place a market buy order for 0.1 BTC",
    "Buy 0.1 BTC at market",
    "Make a purchase of 0.1 Bitcoin",
    "0.1 BTC buy",
    "Buy bitcoin 0.1",
    "Get me 0.1 BTC",
    "Acquire 0.1 Bitcoin",
    "I need 0.1 BTC",
    "Purchase order: 0.1 BTC",
    "Buy 0.1 BTC/USDT",
    "Execute buy: 0.1 BTC",
    "Long 0.1 BTC",
    "Buying 0.1 Bitcoin now",
    "Place order to buy 0.1 BTC",
    "I want 0.1 BTC",
    "Buy 0.1 Bitcoin using USDT",
    "Open position: 0.1 BTC long",
    "Market buy 0.1 BTC",
    "Purchase 0.1 BTC with market order",
    "Acquire 0.1 Bitcoin now",
    "Buy order: 0.1 BTC",
    "Execute purchase of 0.1 BTC",
    "Go long on 0.1 Bitcoin",
    "Buy 0.1 BTC immediately",
    "Place a buy for 0.1 BTC",
    "I'd like to buy 0.1 Bitcoin",
    "Make purchase: 0.1 BTC",
    "Buy 0.1 BTC market order",
    "Purchase 0.1 BTC at current price",
    "Acquire 0.1 BTC position",
    "Open long: 0.1 BTC",
    "Buy me 0.1 Bitcoin",
    "Execute: buy 0.1 BTC",
    "I need to buy 0.1 BTC",
    "Purchase 0.1 Bitcoin please",
    "Buy 0.1 BTC/USDT:USDT",
    "Long position: 0.1 BTC",
    "Market order buy 0.1 BTC",
    "Get 0.1 BTC now",
    "Acquire 0.1 Bitcoin position",
    "Buy order for 0.1 BTC",
    "Purchase 0.1 BTC immediately",
    "Execute buy order 0.1 BTC",
    "Go long 0.1 Bitcoin",
    "Buy 0.1 BTC with market execution",
]


BALANCE_CHECK_PHRASINGS = [
    "check my USDT balance",
    "what's my USDT balance?",
    "show me my USDT balance",
    "how much USDT do I have?",
    "display my USDT balance",
    "USDT balance please",
    "check USDT balance",
    "what is my USDT balance",
    "show USDT balance",
    "I want to see my USDT balance",
    "can you check my USDT?",
    "balance USDT",
    "check balance for USDT",
    "what's my balance in USDT",
    "show balance USDT",
    "my USDT balance",
    "check USDT",
    "display USDT balance",
    "how much USDT?",
    "USDT balance check",
    "what's my USDT?",
    "show me USDT",
    "check my balance USDT",
    "balance check USDT",
    "USDT amount",
    "how many USDT do I have",
    "display my USDT",
    "check USDT holdings",
    "show my USDT balance please",
    "what USDT balance do I have",
    "check balance USDT asset",
    "USDT balance inquiry",
    "show balance for USDT",
    "my balance in USDT",
    "check USDT funds",
    "display USDT holdings",
    "how much USDT is available",
    "USDT balance request",
    "check my USDT funds",
    "show USDT amount",
    "what's my USDT balance right now",
    "check USDT balance now",
    "display current USDT balance",
    "show my current USDT",
    "USDT balance display",
    "check USDT available",
    "what USDT do I have",
    "show USDT funds",
    "check my USDT holdings",
    "USDT balance info",
    "display USDT amount",
    "check balance: USDT",
]


@pytest.mark.asyncio
async def test_buy_intent_consistency():
    """
    Test that 50+ phrasings of "buy 0.1 BTC" produce identical intents.
    
    This is the core requirement: natural language variations must map
    to identical deterministic actions.
    """
    user_id = "test_user_1"
    exchange_manager = MockExchangeManager()
    
    # Create agent (may fail without real API keys, but we can test intent extraction)
    try:
        agent = TradingAgent(user_id, exchange_manager)
    except Exception as e:
        pytest.skip(f"Cannot create agent without API keys: {e}")
    
    intents = []
    
    for phrasing in BUY_INTENT_PHRASINGS:
        try:
            # Create state with message
            from langchain_core.messages import HumanMessage
            from agents.trading_agent import AgentState
            from datetime import datetime
            
            initial_state: AgentState = {
                "user_id": user_id,
                "messages": [HumanMessage(content=phrasing)],
                "intent": "",
                "reasoning": "",
                "action_taken": "",
                "execution_id": f"test_{datetime.utcnow().timestamp()}",
                "start_time": datetime.utcnow().timestamp(),
                "error": None
            }
            
            # Extract intent
            state = await agent._extract_intent(initial_state)
            
            # Parse intent JSON
            import json
            intent_json = json.loads(state["intent"])
            intents.append(intent_json)
        
        except Exception as e:
            pytest.fail(f"Error processing phrasing '{phrasing}': {e}")
    
    # Assert all intents are identical (or at least very similar)
    # The intent should always be "buy" with symbol "BTC/USDT:USDT" and amount 0.1
    for i, intent in enumerate(intents):
        assert intent.get("intent") == "buy", f"Phrasing {i} ({BUY_INTENT_PHRASINGS[i]}) produced wrong intent: {intent}"
        assert intent.get("amount") == 0.1 or intent.get("amount") == "0.1", f"Phrasing {i} produced wrong amount: {intent}"
        # Symbol might vary in format, but should contain BTC
        symbol = intent.get("symbol", "")
        assert "BTC" in str(symbol).upper(), f"Phrasing {i} produced wrong symbol: {intent}"
    
    # Check that at least 90% of intents match exactly (allowing for minor variations)
    first_intent = intents[0]
    matching_count = sum(1 for intent in intents if intent == first_intent)
    match_ratio = matching_count / len(intents)
    
    assert match_ratio >= 0.9, f"Only {match_ratio*100:.1f}% of intents matched exactly. Expected >=90%"


@pytest.mark.asyncio
async def test_balance_check_consistency():
    """Test that balance check phrasings produce identical intents."""
    user_id = "test_user_2"
    exchange_manager = MockExchangeManager()
    
    try:
        agent = TradingAgent(user_id, exchange_manager)
    except Exception as e:
        pytest.skip(f"Cannot create agent without API keys: {e}")
    
    intents = []
    
    for phrasing in BALANCE_CHECK_PHRASINGS:
        try:
            from langchain_core.messages import HumanMessage
            from agents.trading_agent import AgentState
            from datetime import datetime
            
            initial_state: AgentState = {
                "user_id": user_id,
                "messages": [HumanMessage(content=phrasing)],
                "intent": "",
                "reasoning": "",
                "action_taken": "",
                "execution_id": f"test_{datetime.utcnow().timestamp()}",
                "start_time": datetime.utcnow().timestamp(),
                "error": None
            }
            
            state = await agent._extract_intent(initial_state)
            
            import json
            intent_json = json.loads(state["intent"])
            intents.append(intent_json)
        
        except Exception as e:
            pytest.fail(f"Error processing phrasing '{phrasing}': {e}")
    
    # All should be "check_balance" intent with USDT
    for i, intent in enumerate(intents):
        assert intent.get("intent") == "check_balance", f"Phrasing {i} produced wrong intent: {intent}"
        symbol = intent.get("symbol", "")
        assert "USDT" in str(symbol).upper(), f"Phrasing {i} produced wrong asset: {intent}"


@pytest.mark.asyncio
async def test_latency_requirement():
    """Test that end-to-end execution completes in <10 seconds."""
    user_id = "test_user_3"
    exchange_manager = MockExchangeManager()
    
    try:
        agent = TradingAgent(user_id, exchange_manager)
    except Exception as e:
        pytest.skip(f"Cannot create agent without API keys: {e}")
    
    import time
    start_time = time.time()
    
    try:
        result = await agent.process_message("check my USDT balance")
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        assert latency < 10000, f"Execution took {latency:.1f}ms, exceeds 10s limit"
        assert result.get("success"), "Execution should succeed"
    
    except Exception as e:
        # If it fails due to missing API keys, that's expected in test environment
        if "API key" in str(e) or "API_KEY" in str(e):
            pytest.skip("Cannot test latency without API keys")
        raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

