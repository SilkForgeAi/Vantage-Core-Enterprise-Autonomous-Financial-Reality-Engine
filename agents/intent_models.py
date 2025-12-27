"""Pydantic models for deterministic intent extraction."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from agents.symbol_normalizer import SymbolNormalizer


class TradingIntent(BaseModel):
    """
    Structured intent model for deterministic parsing.
    
    This ensures that 50+ phrasings of the same intent produce identical structured outputs.
    """
    intent: Literal["buy", "sell", "check_balance", "check_position", "cancel_order", "unknown"] = Field(
        description="The trading intent type"
    )
    symbol: Optional[str] = Field(
        default=None,
        description="Trading symbol (e.g., 'BTC/USDT:USDT', 'ETH/USDT:USDT')"
    )
    amount: Optional[float] = Field(
        default=None,
        description="Order amount (for buy/sell intents)"
    )
    side: Optional[Literal["buy", "sell"]] = Field(
        default=None,
        description="Order side (for buy/sell intents)"
    )
    asset: Optional[str] = Field(
        default=None,
        description="Asset symbol for balance checks (e.g., 'USDT', 'BTC')"
    )
    details: Optional[str] = Field(
        default=None,
        description="Any additional details or context"
    )
    
    @field_validator('symbol', mode='before')
    @classmethod
    def normalize_symbol(cls, v):
        """Normalize symbol to ensure consistency."""
        if v:
            return SymbolNormalizer.normalize(str(v))
        return v
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "intent": self.intent,
            "symbol": self.symbol,
            "amount": self.amount,
            "side": self.side,
            "asset": self.asset,
            "details": self.details
        }

