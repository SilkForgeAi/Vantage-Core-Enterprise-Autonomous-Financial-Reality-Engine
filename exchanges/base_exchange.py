"""Base exchange interface for unified exchange management."""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from enum import Enum


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


@dataclass
class Balance:
    """Unified balance representation."""
    asset: str
    free: float
    locked: float
    total: float


@dataclass
class Position:
    """Unified position representation."""
    symbol: str
    size: float
    side: str  # "long" or "short"
    entry_price: float
    unrealized_pnl: float
    leverage: Optional[float] = None


@dataclass
class OrderRequest:
    """Unified order request format."""
    symbol: str
    side: OrderSide
    order_type: OrderType
    amount: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    reduce_only: bool = False


@dataclass
class OrderFill:
    """Order fill confirmation."""
    order_id: str
    symbol: str
    side: str
    amount: float
    price: float
    fee: float
    timestamp: float
    exchange: str


class BaseExchange(ABC):
    """Abstract base class for exchange integrations."""
    
    def __init__(self, exchange_name: str, api_key: str, api_secret: str, sandbox: bool = False):
        self.exchange_name = exchange_name
        self.api_key = api_key
        self.api_secret = api_secret
        self.sandbox = sandbox
    
    @abstractmethod
    async def connect(self):
        """Initialize exchange connection."""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Close exchange connection."""
        pass
    
    @abstractmethod
    async def fetch_balances(self) -> Dict[str, Balance]:
        """
        Fetch current balances.
        
        Returns:
            Dict of {asset: Balance}
        """
        pass
    
    @abstractmethod
    async def fetch_positions(self) -> Dict[str, Position]:
        """
        Fetch current positions.
        
        Returns:
            Dict of {symbol: Position}
        """
        pass
    
    @abstractmethod
    async def place_order(self, order: OrderRequest) -> OrderFill:
        """
        Place an order and return fill confirmation.
        
        Returns:
            OrderFill with execution details
        """
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an order."""
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker/price for a symbol."""
        pass
    
    @abstractmethod
    async def start_websocket_feed(self, callback):
        """
        Start WebSocket feed for real-time updates.
        
        Args:
            callback: Async function to call with updates
        """
        pass

