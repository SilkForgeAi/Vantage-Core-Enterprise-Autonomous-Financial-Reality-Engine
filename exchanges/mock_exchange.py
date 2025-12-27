"""Mock exchange for demonstrations without real API keys."""
from typing import Dict, Any
from datetime import datetime
import structlog
from exchanges.base_exchange import (
    BaseExchange, Balance, Position, OrderRequest, OrderFill,
    OrderSide, OrderType
)


logger = structlog.get_logger()


class MockExchange(BaseExchange):
    """
    Mock exchange for safe demonstrations.
    
    Returns realistic mock data without connecting to real exchanges.
    Perfect for demos, testing, and development.
    """
    
    def __init__(self, exchange_name: str, api_key: str = "", api_secret: str = "", sandbox: bool = True):
        super().__init__(exchange_name, api_key, api_secret, sandbox)
        self._mock_balances = {
            "USDT": Balance(asset="USDT", free=10000.0, locked=0.0, total=10000.0),
            "BTC": Balance(asset="BTC", free=0.5, locked=0.0, total=0.5),
            "ETH": Balance(asset="ETH", free=10.0, locked=0.0, total=10.0),
        }
        self._mock_positions: Dict[str, Position] = {}
        self._order_counter = 0
    
    async def connect(self):
        """Mock connection - always succeeds."""
        logger.info(f"Mock exchange {self.exchange_name} connected (DEMO MODE)")
    
    async def disconnect(self):
        """Mock disconnect."""
        logger.info(f"Mock exchange {self.exchange_name} disconnected")
    
    async def fetch_balances(self) -> Dict[str, Balance]:
        """Return mock balances."""
        return self._mock_balances.copy()
    
    async def fetch_positions(self) -> Dict[str, Position]:
        """Return mock positions."""
        return self._mock_positions.copy()
    
    async def place_order(self, order: OrderRequest) -> OrderFill:
        """
        Mock order placement - simulates execution without real trades.
        
        Updates mock balances and creates a fill confirmation.
        """
        self._order_counter += 1
        order_id = f"mock_order_{self._order_counter}_{int(datetime.utcnow().timestamp())}"
        
        # Simulate execution
        import asyncio
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Get current price (mock)
        mock_price = 45000.0 if "BTC" in order.symbol else 2500.0
        
        # Calculate fill amount and fees
        filled_amount = order.amount
        fee = filled_amount * mock_price * 0.001  # 0.1% fee
        
        # Update mock balances (simplified)
        if order.side == OrderSide.BUY:
            # Deduct quote currency, add base currency
            quote_currency = order.symbol.split("/")[-1].split(":")[0]
            cost = filled_amount * mock_price
            if quote_currency in self._mock_balances:
                self._mock_balances[quote_currency].free -= cost
                self._mock_balances[quote_currency].total -= cost
        else:
            # Deduct base currency, add quote currency
            base_currency = order.symbol.split("/")[0]
            proceeds = filled_amount * mock_price
            quote_currency = order.symbol.split("/")[-1].split(":")[0]
            if quote_currency in self._mock_balances:
                self._mock_balances[quote_currency].free += proceeds
                self._mock_balances[quote_currency].total += proceeds
        
        logger.info(
            f"Mock order executed",
            order_id=order_id,
            symbol=order.symbol,
            side=order.side.value,
            amount=filled_amount,
            price=mock_price
        )
        
        return OrderFill(
            order_id=order_id,
            symbol=order.symbol,
            side=order.side.value,
            amount=filled_amount,
            price=mock_price,
            fee=fee,
            timestamp=datetime.utcnow().timestamp(),
            exchange=f"{self.exchange_name}_MOCK"
        )
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Mock order cancellation."""
        logger.info(f"Mock order cancelled", order_id=order_id, symbol=symbol)
        return True
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Return mock ticker data."""
        base_price = 45000.0 if "BTC" in symbol else 2500.0
        return {
            'symbol': symbol,
            'last': base_price,
            'bid': base_price * 0.9999,
            'ask': base_price * 1.0001,
            'volume': 1000.0,
            'timestamp': datetime.utcnow().timestamp() * 1000
        }
    
    async def start_websocket_feed(self, callback):
        """Mock WebSocket feed - sends periodic updates."""
        import asyncio
        self._ws_running = True
        
        while self._ws_running:
            try:
                balances = await self.fetch_balances()
                positions = await self.fetch_positions()
                await callback({
                    'type': 'update',
                    'balances': balances,
                    'positions': positions,
                    'timestamp': datetime.utcnow().timestamp()
                })
            except Exception as e:
                logger.error(f"Error in mock WebSocket feed", error=str(e))
            
            await asyncio.sleep(1.0)  # Update every second

