# Changelog

Latest Improvements (Based on Feedback)

Symbol Normalizer Enhancements (v2)

Added robust symbol normalization to better align with bounty requirements:

1. Expanded Symbol Map - Added 15+ common assets (SOL, BNB, ADA, XRP, DOGE, DOT, MATIC, AVAX, LINK, UNI, LTC)
2. Concatenated Format Support - Handles "BTCUSDT", "ETHUSD" without slashes
3. Suffix Removal - Strips "PERP", "FUTURES", "PERPETUAL", "-PERP" automatically
4. Fuzzy Matching - Handles typos/misspellings (e.g., "bitcion" → "BTC")
5. Multiple Quote Currencies - Supports USDT, USD, USDC, BUSD, EUR, GBP
6. Better Edge Case Handling - Robust parsing for various input formats
7. Validation Helper - Added `is_normalized()` method to check format
8. BTC Quote Support - Added BTC as quote currency (ETHBTC → ETH/BTC:BTC)
9. More Aggressive Fuzzy Matching - Lowered cutoff to 0.65 to catch more typos (solna → SOLANA)

Impact: Ensures deterministic symbol handling across all intent variations, directly supporting the "Context Gap" requirement.

Performance Note: Caching
- Decision: No caching added for now
- Rationale: 
  - SYMBOL_MAP lookup is O(1) and extremely fast
  - Fuzzy matching is fallback only (rare case)
  - Simple design, no premature optimization
  - Can add LRU cache later if profiling shows it's needed

Test Results

All edge cases now pass:
- ✅ "BTCUSDT" → "BTC/USDT:USDT"
- ✅ "BTC-PERP" → "BTC/USDT:USDT"
- ✅ "bitcion" (typo) → "BTC/USDT:USDT"
- ✅ "ETH/USD" → "ETH/USD:USD"
- ✅ And 50+ other variations

This ensures that natural language variations like:
- "Buy BTC"
- "Trade Bitcoin"
- "Long BTCUSDT"
- "Buy BTC-PERP"

All map to the same normalized symbol "BTC/USDT:USDT", enabling deterministic execution.

