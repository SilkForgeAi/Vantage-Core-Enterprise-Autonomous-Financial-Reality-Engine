"""Setup script for the trading agent."""
import os
from security.encryption import generate_master_key


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if os.path.exists(".env"):
        print(".env file already exists")
        return
    
    # Generate encryption key
    encryption_key = generate_master_key()
    
    env_template = f"""# LLM API Keys (at least one required)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Redis Connection
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Database
DATABASE_URL=sqlite:///./trading_agent.db

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# Encryption Key (auto-generated)
ENCRYPTION_KEY={encryption_key}

# Exchange API Keys (format: EXCHANGE_NAME_API_KEY, EXCHANGE_NAME_API_SECRET)
BINANCE_API_KEY=
BINANCE_API_SECRET=
BYBIT_API_KEY=
BYBIT_API_SECRET=
ALPACA_API_KEY=
ALPACA_API_SECRET=

# Agent Configuration
MAX_EXECUTION_TIME_SECONDS=10
DEFAULT_MODEL=claude-3-5-sonnet-20241022
ENABLE_LIVE_TRADING=false  # Set to true only when ready for real money
DEMO_MODE=false  # Set to true for safe demonstrations (uses mock exchanges)

# Logging
LOG_LEVEL=INFO
AUDIT_LOG_DIR=./audit_logs
"""
    
    with open(".env", "w") as f:
        f.write(env_template)
    
    print(".env file created successfully!")
    print(f"Generated encryption key: {encryption_key}")
    print("\nPlease edit .env and add your API keys before running the application.")


if __name__ == "__main__":
    create_env_file()

