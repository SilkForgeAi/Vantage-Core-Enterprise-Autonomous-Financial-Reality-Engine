"""FastAPI backend for multi-user trading agent."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional, List
import structlog
from datetime import datetime
import asyncio

from config.settings import settings
from storage.state_manager import state_manager
from storage.memory_manager import memory_manager
from security.encryption import KeyEncryption
from exchanges.exchange_manager import ExchangeManager
from agents.trading_agent import TradingAgent
from backend.state_sync import StateSyncService


logger = structlog.get_logger()

app = FastAPI(title="AI Trading Agent API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
encryption = KeyEncryption(settings.encryption_key)
exchange_managers: Dict[str, ExchangeManager] = {}  # Per-user exchange managers
trading_agents: Dict[str, TradingAgent] = {}  # Per-user agents
state_sync_service: Optional[StateSyncService] = None


@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    await state_manager.connect()
    memory_manager.connect()
    
    # Start state sync service
    global state_sync_service
    state_sync_service = StateSyncService(exchange_managers)
    await state_sync_service.start()
    
    logger.info("Backend started")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    # Stop state sync service
    global state_sync_service
    if state_sync_service:
        await state_sync_service.stop()
    
    # Disconnect all exchanges
    for user_id, em in exchange_managers.items():
        await em.disconnect_all(user_id)
    
    await state_manager.disconnect()
    logger.info("Backend shutdown")


class AddExchangeRequest(BaseModel):
    """Request to add an exchange for a user."""
    user_id: str
    exchange_name: str
    encrypted_api_key: str
    encrypted_api_secret: str


class MessageRequest(BaseModel):
    """Request to process a message."""
    user_id: str
    message: str


class UserResponse(BaseModel):
    """Response with user data."""
    user_id: str
    exchanges: List[str]
    status: str


@app.post("/api/user/add_exchange")
async def add_exchange(request: AddExchangeRequest):
    """Add an exchange connection for a user."""
    if request.user_id not in exchange_managers:
        exchange_managers[request.user_id] = ExchangeManager(encryption)
        trading_agents[request.user_id] = TradingAgent(
            request.user_id,
            exchange_managers[request.user_id]
        )
    
    await exchange_managers[request.user_id].add_exchange(
        request.user_id,
        request.exchange_name,
        request.encrypted_api_key,
        request.encrypted_api_secret
    )
    
    # Sync initial state
    await _sync_user_state(request.user_id)
    
    mode = "MOCK (demo)" if settings.demo_mode else ("SANDBOX" if not settings.enable_live_trading else "LIVE")
    return {
        "status": "success",
        "exchange": request.exchange_name,
        "mode": mode,
        "warning": "DEMO MODE - No real trades" if settings.demo_mode else None
    }


@app.post("/api/agent/message")
async def process_message(request: MessageRequest):
    """
    Process a user message through the trading agent.
    
    This is the main entry point. Must complete in <10 seconds.
    
    Key requirements:
    - Zero follow-up questions (fully autonomous)
    - Deterministic execution (same intent → same outcome)
    - Sub-10s latency
    """
    # Validate input
    if not request.user_id or not request.message:
        raise HTTPException(status_code=400, detail="user_id and message are required")
    
    # Auto-initialize demo user in demo mode
    if request.user_id not in trading_agents:
        if settings.demo_mode:
            # Create demo user with mock exchanges automatically
            exchange_managers[request.user_id] = ExchangeManager(encryption)
            trading_agents[request.user_id] = TradingAgent(
                request.user_id,
                exchange_managers[request.user_id]
            )
            # Add mock exchanges
            dummy_key = encryption.encrypt("demo_key")
            dummy_secret = encryption.encrypt("demo_secret")
            for exch_name in ["binance", "bybit"]:
                try:
                    await exchange_managers[request.user_id].add_exchange(
                        request.user_id,
                        exch_name,
                        dummy_key,
                        dummy_secret
                    )
                except:
                    pass
        else:
            raise HTTPException(
                status_code=404,
                detail="User not initialized. Add exchanges first via /api/user/add_exchange"
            )
    
    agent = trading_agents[request.user_id]
    
    try:
        # Process message (fully autonomous, no follow-ups)
        result = await agent.process_message(request.message)
        
        # Validate result structure
        if not result.get("execution_id"):
            logger.warning(f"Result missing execution_id", user_id=request.user_id)
        
        # Log if latency exceeds threshold
        latency_ms = result.get("latency_ms", 0)
        if latency_ms > settings.max_execution_time_seconds * 1000:
            logger.warning(
                f"Execution exceeded time limit",
                user_id=request.user_id,
                latency_ms=latency_ms,
                limit_ms=settings.max_execution_time_seconds * 1000
            )
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error processing message", user_id=request.user_id, error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing message", user_id=request.user_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.get("/api/user/{user_id}/status")
async def get_user_status(user_id: str):
    """Get user status including connected exchanges."""
    if user_id not in exchange_managers:
        return UserResponse(
            user_id=user_id,
            exchanges=[],
            status="not_initialized"
        )
    
    exchanges = exchange_managers[user_id].get_user_exchanges(user_id)
    return UserResponse(
        user_id=user_id,
        exchanges=exchanges,
        status="active"
    )


@app.get("/api/user/{user_id}/balances")
async def get_balances(user_id: str):
    """Get unified balances for a user."""
    if user_id not in exchange_managers:
        raise HTTPException(status_code=404, detail="User not initialized")
    
    balances = await exchange_managers[user_id].get_unified_balances(user_id)
    return {"user_id": user_id, "balances": balances}


@app.get("/api/user/{user_id}/positions")
async def get_positions(user_id: str):
    """Get unified positions for a user."""
    if user_id not in exchange_managers:
        raise HTTPException(status_code=404, detail="User not initialized")
    
    positions = await exchange_managers[user_id].get_unified_positions(user_id)
    return {"user_id": user_id, "positions": positions}


async def _sync_user_state(user_id: str):
    """Sync state from exchanges to Redis."""
    if user_id not in exchange_managers:
        return
    
    em = exchange_managers[user_id]
    
    # Sync balances
    unified_balances = await em.get_unified_balances(user_id)
    for exchange_name, balances in unified_balances.items():
        balance_dict = {asset: bal.total for asset, bal in balances.items()}
        await state_manager.set_balance(user_id, exchange_name, balance_dict)
    
    # Sync positions
    unified_positions = await em.get_unified_positions(user_id)
    for exchange_name, positions in unified_positions.items():
        for symbol, position in positions.items():
            await state_manager.set_position(
                user_id,
                exchange_name,
                symbol,
                {
                    "size": position.size,
                    "side": position.side,
                    "entry_price": position.entry_price,
                    "unrealized_pnl": position.unrealized_pnl
                }
            )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "service": "AI Trading Agent",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

