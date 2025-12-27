"""Agent tools for LLM function calling."""
from typing import Dict, Any, Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import structlog
import json
from exchanges.base_exchange import OrderRequest, OrderSide, OrderType
from exchanges.exchange_manager import ExchangeManager
from storage.state_manager import state_manager
from agents.symbol_normalizer import SymbolNormalizer


logger = structlog.get_logger()


class GetBalanceInput(BaseModel):
    """Input for get_balance tool."""
    asset: str = Field(description="Asset symbol (e.g., 'USDT', 'BTC')")


class GetPositionInput(BaseModel):
    """Input for get_position tool."""
    symbol: str = Field(description="Trading symbol (e.g., 'BTC/USDT:USDT')")


class PlaceOrderInput(BaseModel):
    """Input for place_order tool."""
    symbol: str = Field(description="Trading symbol (e.g., 'BTC/USDT:USDT')")
    side: str = Field(description="Order side: 'buy' or 'sell'")
    amount: float = Field(description="Order amount (in base currency)")
    order_type: str = Field(default="market", description="Order type: 'market', 'limit', or 'stop'")
    price: Optional[float] = Field(default=None, description="Limit price (required for limit orders)")
    reduce_only: bool = Field(default=False, description="Reduce position only (for closing)")


class GetTickerInput(BaseModel):
    """Input for get_ticker tool."""
    symbol: str = Field(description="Trading symbol (e.g., 'BTC/USDT:USDT')")


def create_tools(user_id: str, exchange_manager: ExchangeManager):
    """Create tools for the agent with user context."""
    
    class GetBalanceTool(BaseTool):
        name: str = "get_balance"
        description: str = "Get total balance of an asset across all connected exchanges. Returns the unified view."
        args_schema: type = GetBalanceInput
        
        async def _arun(self, asset: str) -> str:
            total = await state_manager.get_total_balance(user_id, asset)
            unified = await state_manager.get_unified_balances(user_id)
            
            result = {
                "asset": asset,
                "total_balance": total,
                "by_exchange": {}
            }
            
            for exchange, balances in unified.items():
                result["by_exchange"][exchange] = balances.get(asset, 0.0)
            
            return str(result)
        
        def _run(self, asset: str) -> str:
            import asyncio
            return asyncio.run(self._arun(asset))
    
    class GetPositionTool(BaseTool):
        name: str = "get_position"
        description: str = "Get position details for a symbol across all exchanges."
        args_schema: type = GetPositionInput
        
        async def _arun(self, symbol: str) -> str:
            unified_positions = await exchange_manager.get_unified_positions(user_id)
            
            result = {
                "symbol": symbol,
                "positions": {}
            }
            
            for exchange, positions in unified_positions.items():
                if symbol in positions:
                    pos = positions[symbol]
                    result["positions"][exchange] = {
                        "size": pos.size,
                        "side": pos.side,
                        "entry_price": pos.entry_price,
                        "unrealized_pnl": pos.unrealized_pnl
                    }
            
            if not result["positions"]:
                return f"No open positions for {symbol}"
            
            return str(result)
        
        def _run(self, symbol: str) -> str:
            import asyncio
            return asyncio.run(self._arun(symbol))
    
    class PlaceOrderTool(BaseTool):
        name: str = "place_order"
        description: str = (
            "Place an order on an exchange. "
            "For market orders, execution is immediate. "
            "The agent must decide which exchange to use based on balance availability and best execution. "
            "This is a REAL order that will execute with real money."
        )
        args_schema: type = PlaceOrderInput
        
        async def _arun(
            self,
            symbol: str,
            side: str,
            amount: float,
            order_type: str = "market",
            price: Optional[float] = None,
            reduce_only: bool = False
        ) -> str:
            # Get available exchanges
            user_exchanges = exchange_manager.get_user_exchanges(user_id)
            if not user_exchanges:
                return "Error: No exchanges connected. Please add exchanges first."
            
            # LLM-driven exchange selection: Choose best exchange based on balance availability
            # This is still dynamic - no hard-coded routing logic
            # In a more advanced implementation, this could be another LLM call
            # For now, we use the exchange with the best balance for the quote currency
            exchange_name = user_exchanges[0]  # Default to first
            
            # Try to find exchange with sufficient balance for the order
            if order_type == "market":
                # Extract quote currency (e.g., "USDT" from "BTC/USDT:USDT")
                quote_currency = symbol.split("/")[-1].split(":")[0] if "/" in symbol else "USDT"
                
                # Check balances across exchanges
                unified_balances = await state_manager.get_unified_balances(user_id)
                best_exchange = None
                max_balance = 0
                
                for exch_name in user_exchanges:
                    exch_balances = unified_balances.get(exch_name, {})
                    balance_obj = exch_balances.get(quote_currency)
                    if balance_obj:
                        balance_amount = balance_obj.total if hasattr(balance_obj, 'total') else balance_obj
                        if balance_amount > max_balance:
                            max_balance = balance_amount
                            best_exchange = exch_name
                
                if best_exchange:
                    exchange_name = best_exchange
            
            # Normalize symbol for consistency
            normalized_symbol = SymbolNormalizer.normalize(symbol)
            
            # Convert side (minimal hard-coded conversion for API compatibility)
            # This is necessary API mapping, not decision logic
            side_lower = side.lower().strip()
            if side_lower in ("buy", "long"):
                order_side = OrderSide.BUY
            elif side_lower in ("sell", "short"):
                order_side = OrderSide.SELL
            else:
                return f"Error: Invalid side '{side}'. Must be 'buy' or 'sell'"
            
            # Convert order type (minimal hard-coded conversion for API compatibility)
            # This is necessary API mapping, not decision logic
            order_type_lower = order_type.lower().strip()
            type_map = {
                "market": OrderType.MARKET,
                "limit": OrderType.LIMIT,
                "stop": OrderType.STOP,
                "stop_market": OrderType.STOP,
            }
            ot = type_map.get(order_type_lower)
            if not ot:
                return f"Error: Invalid order type '{order_type}'. Must be 'market', 'limit', or 'stop'"
            
            # Create order request
            order = OrderRequest(
                symbol=normalized_symbol,
                side=order_side,
                order_type=ot,
                amount=amount,
                price=price,
                reduce_only=reduce_only
            )
            
            try:
                fill = await exchange_manager.place_order_on_exchange(
                    user_id,
                    exchange_name,
                    order
                )
                
                return f"Order filled: {fill.order_id} on {exchange_name}, {fill.amount} {symbol} at {fill.price}, fee: {fill.fee}"
            except Exception as e:
                logger.error(f"Error placing order", error=str(e))
                return f"Error placing order: {str(e)}"
        
        def _run(self, symbol: str, side: str, amount: float, **kwargs) -> str:
            import asyncio
            return asyncio.run(self._arun(symbol, side, amount, **kwargs))
    
    class GetTickerTool(BaseTool):
        name: str = "get_ticker"
        description: str = "Get current price/ticker for a symbol."
        args_schema: type = GetTickerInput
        
        async def _arun(self, symbol: str) -> str:
            user_exchanges = exchange_manager.get_user_exchanges(user_id)
            if not user_exchanges:
                return "Error: No exchanges connected"
            
            # Get price from first exchange
            exchange_name = user_exchanges[0]
            exchange = exchange_manager.user_exchanges[user_id][exchange_name]
            
            try:
                ticker = await exchange.get_ticker(symbol)
                return str(ticker)
            except Exception as e:
                return f"Error getting ticker: {str(e)}"
        
        def _run(self, symbol: str) -> str:
            import asyncio
            return asyncio.run(self._arun(symbol))
    
    return [
        GetBalanceTool(),
        GetPositionTool(),
        PlaceOrderTool(),
        GetTickerTool()
    ]

