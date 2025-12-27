"""Unified cross-venue state management with Redis."""
import redis.asyncio as redis
import json
from typing import Dict, Optional, Any
from datetime import datetime
import structlog
from config.settings import settings


logger = structlog.get_logger()


class UnifiedStateManager:
    """
    Manages unified cross-venue state per user.
    
    Key principle: The agent's "proprioception" - self-awareness of position/state
    across all connected exchanges in real-time.
    """
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection."""
        self.redis_client = await redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True
        )
        logger.info("Connected to Redis for state management")
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.aclose()
    
    def _user_key(self, user_id: str, key: str) -> str:
        """Generate a namespaced Redis key for a user."""
        return f"user:{user_id}:{key}"
    
    async def set_balance(self, user_id: str, exchange: str, balance: Dict[str, float]):
        """
        Set balance for a specific exchange.
        
        Args:
            user_id: User identifier
            exchange: Exchange name (e.g., 'binance', 'bybit')
            balance: Dict of {asset: balance_amount}
        """
        key = self._user_key(user_id, f"balance:{exchange}")
        await self.redis_client.setex(
            key,
            300,  # 5 minute TTL
            json.dumps({
                "exchange": exchange,
                "balances": balance,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    async def get_balance(self, user_id: str, exchange: str) -> Optional[Dict[str, float]]:
        """Get balance for a specific exchange."""
        key = self._user_key(user_id, f"balance:{exchange}")
        data = await self.redis_client.get(key)
        if data:
            parsed = json.loads(data)
            return parsed.get("balances")
        return None
    
    async def get_unified_balances(self, user_id: str) -> Dict[str, Dict[str, float]]:
        """
        Get all balances across all exchanges for a user.
        
        Returns:
            Dict of {exchange: {asset: balance}}
        """
        pattern = self._user_key(user_id, "balance:*")
        keys = await self.redis_client.keys(pattern)
        
        unified = {}
        for key in keys:
            data = await self.redis_client.get(key)
            if data:
                parsed = json.loads(data)
                exchange = parsed["exchange"]
                unified[exchange] = parsed["balances"]
        
        return unified
    
    async def get_total_balance(self, user_id: str, asset: str) -> float:
        """
        Get total balance of an asset across all exchanges.
        
        This is the unified view the agent uses for decision-making.
        """
        unified = await self.get_unified_balances(user_id)
        total = 0.0
        
        for exchange_balances in unified.values():
            total += exchange_balances.get(asset, 0.0)
        
        return total
    
    async def set_position(self, user_id: str, exchange: str, symbol: str, position: Dict[str, Any]):
        """Set position for a symbol on an exchange."""
        key = self._user_key(user_id, f"position:{exchange}:{symbol}")
        await self.redis_client.setex(
            key,
            300,
            json.dumps({
                "exchange": exchange,
                "symbol": symbol,
                "position": position,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    async def get_position(self, user_id: str, exchange: str, symbol: str) -> Optional[Dict[str, Any]]:
        """Get position for a symbol on an exchange."""
        key = self._user_key(user_id, f"position:{exchange}:{symbol}")
        data = await self.redis_client.get(key)
        if data:
            parsed = json.loads(data)
            return parsed.get("position")
        return None
    
    async def get_unified_positions(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """Get all positions across all exchanges."""
        pattern = self._user_key(user_id, "position:*")
        keys = await self.redis_client.keys(pattern)
        
        unified = {}
        for key in keys:
            data = await self.redis_client.get(key)
            if data:
                parsed = json.loads(data)
                exchange = parsed["exchange"]
                symbol = parsed["symbol"]
                if exchange not in unified:
                    unified[exchange] = {}
                unified[exchange][symbol] = parsed["position"]
        
        return unified
    
    async def set_risk_profile(self, user_id: str, risk_config: Dict[str, Any]):
        """Set user's risk profile (max position size, leverage limits, etc.)."""
        key = self._user_key(user_id, "risk_profile")
        await self.redis_client.set(
            key,
            json.dumps({
                "config": risk_config,
                "timestamp": datetime.utcnow().isoformat()
            })
        )
    
    async def get_risk_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's risk profile."""
        key = self._user_key(user_id, "risk_profile")
        data = await self.redis_client.get(key)
        if data:
            parsed = json.loads(data)
            return parsed.get("config")
        return None
    
    async def set_execution_state(self, user_id: str, execution_id: str, state: Dict[str, Any]):
        """Store execution state for audit and recovery."""
        key = self._user_key(user_id, f"execution:{execution_id}")
        await self.redis_client.setex(
            key,
            3600,  # 1 hour TTL
            json.dumps(state)
        )
    
    async def get_execution_state(self, user_id: str, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution state."""
        key = self._user_key(user_id, f"execution:{execution_id}")
        data = await self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None


# Global state manager instance
state_manager = UnifiedStateManager()

