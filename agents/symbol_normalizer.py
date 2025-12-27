"""Symbol normalization for deterministic symbol handling."""
from typing import Optional
import re
from difflib import get_close_matches


class SymbolNormalizer:
    """
    Normalizes trading symbols for deterministic handling.
    
    Ensures that "BTC", "Bitcoin", "BTC/USDT", "BTCUSDT" all map to the same standardized format.
    This directly supports the bounty requirement of deterministic intent-to-execution.
    """
    
    # Common symbol mappings - expanded for better coverage
    SYMBOL_MAP = {
        "BTC": "BTC/USDT:USDT",
        "BITCOIN": "BTC/USDT:USDT",
        "ETH": "ETH/USDT:USDT",
        "ETHEREUM": "ETH/USDT:USDT",
        "SOL": "SOL/USDT:USDT",
        "SOLANA": "SOL/USDT:USDT",
        "BNB": "BNB/USDT:USDT",
        "BINANCE": "BNB/USDT:USDT",
        "ADA": "ADA/USDT:USDT",
        "CARDANO": "ADA/USDT:USDT",
        "XRP": "XRP/USDT:USDT",
        "RIPPLE": "XRP/USDT:USDT",
        "DOGE": "DOGE/USDT:USDT",
        "DOGECOIN": "DOGE/USDT:USDT",
        "DOT": "DOT/USDT:USDT",
        "POLKADOT": "DOT/USDT:USDT",
        "MATIC": "MATIC/USDT:USDT",
        "POLYGON": "MATIC/USDT:USDT",
        "AVAX": "AVAX/USDT:USDT",
        "AVALANCHE": "AVAX/USDT:USDT",
        "LINK": "LINK/USDT:USDT",
        "CHAINLINK": "LINK/USDT:USDT",
        "UNI": "UNI/USDT:USDT",
        "UNISWAP": "UNI/USDT:USDT",
        "LTC": "LTC/USDT:USDT",
        "LITECOIN": "LTC/USDT:USDT",
        "USDT": "USDT/USD:USD",
        "USDC": "USDC/USD:USD",
    }
    
    # Supported quote currencies (including BTC for BTC pairs)
    SUPPORTED_QUOTES = {"USDT", "USD", "USDC", "BUSD", "EUR", "GBP", "BTC"}
    
    @staticmethod
    def normalize(symbol: str, quote_currency: Optional[str] = "USDT") -> str:
        """
        Normalize a symbol to standard format with deterministic mapping.
        
        Handles:
        - Direct mappings (BTC → BTC/USDT:USDT)
        - Concatenated formats (BTCUSDT → BTC/USDT:USDT, ETHBTC → ETH/BTC:BTC)
        - Spot formats (BTC/USDT → BTC/USDT:USDT)
        - Futures formats (BTC/USDT:USDT → BTC/USDT:USDT)
        - Typos/misspellings (bitcion → BTC via fuzzy matching)
        - Common suffixes (BTC-PERP → BTC/USDT:USDT)
        
        Args:
            symbol: Input symbol (e.g., "BTC", "BTC/USDT", "BTC/USDT:USDT", "BTCUSDT", "ETHBTC")
            quote_currency: Default quote currency if not specified (default: "USDT")
        
        Returns:
            Normalized symbol in futures format (e.g., "BTC/USDT:USDT")
        """
        if not symbol:
            return ""
        
        # Clean and uppercase
        original_symbol = symbol
        symbol = symbol.strip().upper()
        
        # Check direct mapping first (fastest path)
        if symbol in SymbolNormalizer.SYMBOL_MAP:
            return SymbolNormalizer.SYMBOL_MAP[symbol]
        
        # Remove common suffixes/prefixes (PERP, FUTURES, PERPETUAL, -PERP, etc.)
        symbol_cleaned = re.sub(r'[-_]?(PERP|FUTURES|PERPETUAL|FUT|SWAP)$', '', symbol)
        if symbol_cleaned != symbol:
            symbol = symbol_cleaned
        
        # Try direct mapping again after cleaning
        if symbol in SymbolNormalizer.SYMBOL_MAP:
            return SymbolNormalizer.SYMBOL_MAP[symbol]
        
        # Handle concatenated formats like "BTCUSDT", "ETHUSD", "ETHBTC", etc.
        # Match patterns like: (2-10 letters)(USDT|USD|USDC|BUSD|EUR|GBP|BTC)
        match = re.match(r'^([A-Z]{2,10})(USDT|USD|USDC|BUSD|EUR|GBP|BTC)$', symbol)
        if match:
            base, quote = match.groups()
            # Verify base is a known asset (optional validation)
            if base in SymbolNormalizer.SYMBOL_MAP:
                mapped = SymbolNormalizer.SYMBOL_MAP[base]
                # Extract quote from mapped symbol or use detected quote
                if "/" in mapped:
                    mapped_base = mapped.split("/")[0]
                    return f"{mapped_base}/{quote}:{quote}"
            # If not in map, use as-is (trust the detection)
            return f"{base}/{quote}:{quote}"
        
        # If already in futures format like BTC/USDT:USDT, validate and return
        if ":" in symbol and "/" in symbol:
            # Validate format: BASE/QUOTE:QUOTE
            parts = symbol.split(":")
            if len(parts) == 2:
                base_quote, quote_suffix = parts
                if "/" in base_quote:
                    base, quote = base_quote.split("/", 1)
                    # Ensure quote matches suffix
                    if quote == quote_suffix:
                        return symbol
                    else:
                        # Fix mismatch
                        return f"{base}/{quote_suffix}:{quote_suffix}"
        
        # If in spot format like BTC/USDT, convert to futures
        if "/" in symbol:
            parts = symbol.split("/")
            if len(parts) == 2:
                base, quote = parts
                # Clean base and quote
                base = base.strip()
                quote = quote.strip()
                # Check if base needs mapping
                if base in SymbolNormalizer.SYMBOL_MAP:
                    mapped = SymbolNormalizer.SYMBOL_MAP[base]
                    mapped_base = mapped.split("/")[0] if "/" in mapped else base
                    return f"{mapped_base}/{quote}:{quote}"
                return f"{base}/{quote}:{quote}"
        
        # Try fuzzy matching for typos/misspellings (e.g., "bitcion" → "BITCOIN", "solna" → "SOLANA")
        # Lower cutoff (0.65) catches more typos but still avoids false matches
        if len(symbol) >= 3:  # Only for longer symbols
            close_matches = get_close_matches(
                symbol,
                SymbolNormalizer.SYMBOL_MAP.keys(),
                n=1,
                cutoff=0.65  # 65% similarity threshold (more aggressive to catch typos)
            )
            if close_matches:
                matched_key = close_matches[0]
                return SymbolNormalizer.SYMBOL_MAP[matched_key]
        
        # Fallback: Assume it's a base currency and use default quote
        if quote_currency:
            return f"{symbol}/{quote_currency}:{quote_currency}"
        
        return symbol
    
    @staticmethod
    def extract_base_currency(symbol: str) -> str:
        """
        Extract base currency from normalized symbol.
        
        Args:
            symbol: Normalized symbol (e.g., "BTC/USDT:USDT")
        
        Returns:
            Base currency (e.g., "BTC")
        """
        if not symbol:
            return ""
        
        if "/" in symbol:
            return symbol.split("/")[0].strip()
        return symbol.strip()
    
    @staticmethod
    def extract_quote_currency(symbol: str) -> str:
        """
        Extract quote currency from normalized symbol.
        
        Args:
            symbol: Normalized symbol (e.g., "BTC/USDT:USDT")
        
        Returns:
            Quote currency (e.g., "USDT")
        """
        if not symbol:
            return "USDT"  # Default
        
        # Futures format: BASE/QUOTE:QUOTE
        if ":" in symbol:
            return symbol.split(":")[-1].strip()
        
        # Spot format: BASE/QUOTE
        if "/" in symbol:
            parts = symbol.split("/")
            if len(parts) >= 2:
                return parts[1].strip()
        
        return "USDT"  # Default
    
    @staticmethod
    def is_normalized(symbol: str) -> bool:
        """
        Check if a symbol is already in normalized format.
        
        Args:
            symbol: Symbol to check
        
        Returns:
            True if symbol is in format BASE/QUOTE:QUOTE
        """
        if not symbol:
            return False
        
        # Must have both / and :
        if ":" not in symbol or "/" not in symbol:
            return False
        
        parts = symbol.split(":")
        if len(parts) != 2:
            return False
        
        base_quote, quote_suffix = parts
        if "/" not in base_quote:
            return False
        
        base, quote = base_quote.split("/", 1)
        
        # Quote must match suffix
        return quote == quote_suffix
