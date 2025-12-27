"""CCXT-based exchange implementation."""
import ccxt.async_support as ccxt
from typing import Dict, Optional, Any
from datetime import datetime
import structlog
from exchanges.base_exchange import (
    BaseExchange, Balance, Position, OrderRequest, OrderFill,
    OrderSide, OrderType
)


logger = structlog.get_logger()


class CCXTExchange(BaseExchange):
    """CCXT-based exchange implementation with WebSocket support."""
    
    def __init__(self, exchange_name: str, api_key: str, api_secret: str, sandbox: bool = False):
        super().__init__(exchange_name, api_key, api_secret, sandbox)
        self.exchange: Optional[ccxt.Exchange] = None
        self.ws_client = None
        self._ws_running = False
    
    async def connect(self):
        """Initialize CCXT exchange."""
        exchange_class = getattr(ccxt, self.exchange_name.lower())
        
        self.exchange = exchange_class({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # For perps/futures trading
                'adjustForTimeDifference': True,
            },
            'sandbox': self.sandbox,
        })
        
        # Test connection
        try:
            await self.exchange.load_markets()
            logger.info(f"Connected to {self.exchange_name}", sandbox=self.sandbox)
        except Exception as e:
            logger.error(f"Failed to connect to {self.exchange_name}", error=str(e))
            raise
    
    async def disconnect(self):
        """Close exchange connection."""
        if self._ws_running and self.ws_client:
            await self.ws_client.close()
            self._ws_running = False
        
        if self.exchange:
            await self.exchange.close()
            logger.info(f"Disconnected from {self.exchange_name}")
    
    async def fetch_balances(self) -> Dict[str, Balance]:
        """Fetch current balances."""
        try:
            balance_response = await self.exchange.fetch_balance()
            
            balances = {}
            for asset, amount in balance_response.get('total', {}).items():
                if amount > 0 or asset in ['USDT', 'USD', 'BTC', 'ETH']:  # Include major assets even if 0
                    balances[asset] = Balance(
                        asset=asset,
                        free=balance_response.get('free', {}).get(asset, 0.0),
                        locked=balance_response.get('used', {}).get(asset, 0.0),
                        total=amount
                    )
            
            return balances
        except Exception as e:
            logger.error(f"Error fetching balances from {self.exchange_name}", error=str(e))
            raise
    
    async def fetch_positions(self) -> Dict[str, Position]:
        """Fetch current positions."""
        try:
            positions_response = await self.exchange.fetch_positions()
            
            positions = {}
            for pos_data in positions_response:
                symbol = pos_data.get('symbol')
                if symbol and pos_data.get('contracts', 0) != 0:
                    side = 'long' if pos_data.get('side') == 'long' else 'short'
                    positions[symbol] = Position(
                        symbol=symbol,
                        size=abs(pos_data.get('contracts', 0)),
                        side=side,
                        entry_price=pos_data.get('entryPrice', 0.0),
                        unrealized_pnl=pos_data.get('unrealizedPnl', 0.0),
                        leverage=pos_data.get('leverage')
                    )
            
            return positions
        except Exception as e:
            logger.error(f"Error fetching positions from {self.exchange_name}", error=str(e))
            raise
    
    async def place_order(self, order: OrderRequest) -> OrderFill:
        """Place an order and return fill confirmation."""
        try:
            # Convert to CCXT format
            side = order.side.value
            order_type = order.order_type.value
            
            params = {}
            if order.reduce_only:
                params['reduceOnly'] = True
            
            if order.order_type == OrderType.LIMIT and order.price:
                params['price'] = order.price
            elif order.order_type == OrderType.STOP and order.stop_price:
                params['stopPrice'] = order.stop_price
            
            # Place order
            order_response = await self.exchange.create_order(
                symbol=order.symbol,
                type=order_type,
                side=side,
                amount=order.amount,
                params=params
            )
            
            # Wait for fill (for market orders, this should be immediate)
            # For limit orders, we'd need to poll or use WebSocket
            filled_amount = order_response.get('filled', 0.0)
            if filled_amount == 0.0 and order.order_type == OrderType.MARKET:
                # Market order should fill immediately, wait a bit and check
                import asyncio
                await asyncio.sleep(0.5)
                order_status = await self.exchange.fetch_order(order_response['id'], order.symbol)
                filled_amount = order_status.get('filled', 0.0)
                avg_price = order_status.get('average', order_response.get('price', 0.0))
            else:
                avg_price = order_response.get('average', order_response.get('price', 0.0))
            
            # Get fee information
            fee = order_response.get('fee', {})
            fee_amount = fee.get('cost', 0.0) if isinstance(fee, dict) else 0.0
            
            return OrderFill(
                order_id=order_response['id'],
                symbol=order.symbol,
                side=side,
                amount=filled_amount if filled_amount > 0 else order.amount,
                price=avg_price if avg_price else order_response.get('price', 0.0),
                fee=fee_amount,
                timestamp=datetime.utcnow().timestamp(),
                exchange=self.exchange_name
            )
        except Exception as e:
            logger.error(f"Error placing order on {self.exchange_name}", error=str(e), order=str(order))
            raise
    
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        try:
            await self.exchange.cancel_order(order_id, symbol)
            return True
        except Exception as e:
            logger.error(f"Error canceling order on {self.exchange_name}", error=str(e))
            return False
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker/price for a symbol."""
        try:
            ticker = await self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker.get('last'),
                'bid': ticker.get('bid'),
                'ask': ticker.get('ask'),
                'volume': ticker.get('volume'),
                'timestamp': ticker.get('timestamp')
            }
        except Exception as e:
            logger.error(f"Error fetching ticker from {self.exchange_name}", error=str(e))
            raise
    
    async def start_websocket_feed(self, callback):
        """
        Start WebSocket feed for real-time updates.
        
        Note: CCXT doesn't have native WebSocket support for all exchanges.
        For production, you'd want to use exchange-specific WebSocket libraries
        or CCXT Pro if available.
        """
        # This is a placeholder - actual implementation would depend on the exchange
        # For Binance, you'd use python-binance or similar
        # For Bybit, you'd use pybit or similar
        logger.warning(f"WebSocket feed not fully implemented for {self.exchange_name}")
        self._ws_running = True
        
        # Polling fallback (not ideal, but functional)
        import asyncio
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
                logger.error(f"Error in WebSocket feed loop", error=str(e))
            
            await asyncio.sleep(0.5)  # Poll every 500ms

