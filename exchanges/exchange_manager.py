"""Manager for multiple exchange connections per user."""
from typing import Dict, List, Optional
from exchanges.ccxt_exchange import CCXTExchange
from exchanges.base_exchange import BaseExchange, Balance, Position, OrderRequest, OrderFill
from security.encryption import KeyEncryption
import structlog
from config.settings import settings


logger = structlog.get_logger()


class ExchangeManager:
    """
    Manages multiple exchange connections per user.
    
    Provides unified interface across exchanges for the agent.
    """
    
    def __init__(self, encryption: KeyEncryption):
        self.encryption = encryption
        self.user_exchanges: Dict[str, Dict[str, BaseExchange]] = {}  # {user_id: {exchange_name: exchange}}
    
    async def add_exchange(self, user_id: str, exchange_name: str, encrypted_api_key: str, encrypted_api_secret: str):
        """Add and connect an exchange for a user."""
        # Decrypt credentials
        api_key, api_secret = self.encryption.decrypt_api_key(encrypted_api_key, encrypted_api_secret)
        
        # Create exchange instance
        exchange = CCXTExchange(
            exchange_name=exchange_name,
            api_key=api_key,
            api_secret=api_secret,
            sandbox=not settings.enable_live_trading
        )
        
        await exchange.connect()
        
        # Store in user's exchange dict
        if user_id not in self.user_exchanges:
            self.user_exchanges[user_id] = {}
        
        self.user_exchanges[user_id][exchange_name] = exchange
        logger.info(f"Added exchange {exchange_name} for user {user_id}")
    
    async def remove_exchange(self, user_id: str, exchange_name: str):
        """Remove and disconnect an exchange for a user."""
        if user_id in self.user_exchanges and exchange_name in self.user_exchanges[user_id]:
            exchange = self.user_exchanges[user_id][exchange_name]
            await exchange.disconnect()
            del self.user_exchanges[user_id][exchange_name]
            logger.info(f"Removed exchange {exchange_name} for user {user_id}")
    
    def get_user_exchanges(self, user_id: str) -> List[str]:
        """Get list of exchange names for a user."""
        return list(self.user_exchanges.get(user_id, {}).keys())
    
    async def get_unified_balances(self, user_id: str) -> Dict[str, Dict[str, Balance]]:
        """Get balances across all exchanges for a user."""
        if user_id not in self.user_exchanges:
            return {}
        
        unified = {}
        for exchange_name, exchange in self.user_exchanges[user_id].items():
            try:
                balances = await exchange.fetch_balances()
                unified[exchange_name] = balances
            except Exception as e:
                logger.error(f"Error fetching balances from {exchange_name}", error=str(e))
        
        return unified
    
    async def get_unified_positions(self, user_id: str) -> Dict[str, Dict[str, Position]]:
        """Get positions across all exchanges for a user."""
        if user_id not in self.user_exchanges:
            return {}
        
        unified = {}
        for exchange_name, exchange in self.user_exchanges[user_id].items():
            try:
                positions = await exchange.fetch_positions()
                unified[exchange_name] = positions
            except Exception as e:
                logger.error(f"Error fetching positions from {exchange_name}", error=str(e))
        
        return unified
    
    async def place_order_on_exchange(
        self,
        user_id: str,
        exchange_name: str,
        order: OrderRequest
    ) -> OrderFill:
        """Place an order on a specific exchange."""
        if user_id not in self.user_exchanges or exchange_name not in self.user_exchanges[user_id]:
            raise ValueError(f"Exchange {exchange_name} not connected for user {user_id}")
        
        exchange = self.user_exchanges[user_id][exchange_name]
        return await exchange.place_order(order)
    
    async def get_best_price(self, user_id: str, symbol: str) -> Optional[float]:
        """Get best available price across exchanges (for routing decisions)."""
        if user_id not in self.user_exchanges:
            return None
        
        best_price = None
        for exchange_name, exchange in self.user_exchanges[user_id].items():
            try:
                ticker = await exchange.get_ticker(symbol)
                price = ticker.get('last')
                if price and (best_price is None or price < best_price):
                    best_price = price
            except:
                continue
        
        return best_price
    
    async def disconnect_all(self, user_id: str):
        """Disconnect all exchanges for a user."""
        if user_id in self.user_exchanges:
            for exchange_name, exchange in self.user_exchanges[user_id].items():
                try:
                    await exchange.disconnect()
                except:
                    pass
            del self.user_exchanges[user_id]

