#!/usr/bin/env python3
"""Setup demo mode - creates a user with mock exchanges for safe demonstrations."""
import asyncio
import sys
from security.encryption import KeyEncryption
from config.settings import settings
from exchanges.exchange_manager import ExchangeManager
from agents.trading_agent import TradingAgent
from storage.state_manager import state_manager
from storage.memory_manager import memory_manager


async def setup_demo_user():
    """Set up a demo user with mock exchanges."""
    print("Setting up demo mode...")
    print("=" * 60)
    
    # Enable demo mode
    settings.demo_mode = True
    print("✓ Demo mode enabled (using mock exchanges)")
    
    # Initialize services
    await state_manager.connect()
    memory_manager.connect()
    print("✓ State and memory managers initialized")
    
    # Create encryption (needed for ExchangeManager)
    encryption = KeyEncryption(settings.encryption_key)
    
    # Create exchange manager and agent for demo user
    user_id = "demo_user_1"
    exchange_manager = ExchangeManager(encryption)
    
    # Add mock exchanges (no real API keys needed in demo mode)
    print(f"\nAdding mock exchanges for user: {user_id}")
    
    for exchange_name in ["binance", "bybit"]:
        try:
            # In demo mode, we can use dummy encrypted keys
            dummy_key = encryption.encrypt("demo_key")
            dummy_secret = encryption.encrypt("demo_secret")
            
            await exchange_manager.add_exchange(
                user_id,
                exchange_name,
                dummy_key,
                dummy_secret
            )
            print(f"  ✓ Added mock {exchange_name} exchange")
        except Exception as e:
            print(f"  ✗ Error adding {exchange_name}: {e}")
    
    # Create trading agent
    try:
        agent = TradingAgent(user_id, exchange_manager)
        print(f"  ✓ Created trading agent for {user_id}")
    except Exception as e:
        print(f"  ✗ Error creating agent: {e}")
        print(f"    Make sure LLM API key is set in .env")
        return False
    
    print("\n" + "=" * 60)
    print("Demo setup complete!")
    print("=" * 60)
    print(f"\nDemo user ID: {user_id}")
    print("Mock exchanges: binance, bybit")
    print("\nYou can now test the API with:")
    print(f'  curl -X POST "http://localhost:8000/api/agent/message" \\')
    print(f'    -H "Content-Type: application/json" \\')
    print(f'    -d \'{{"user_id": "{user_id}", "message": "check my USDT balance"}}\'')
    print("\nNote: All trades are simulated - no real money is used!")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(setup_demo_user())
    sys.exit(0 if success else 1)

