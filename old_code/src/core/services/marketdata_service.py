"""
MarketDataService
-----------------
Thin orchestration over the MarketData port:

- Normalizes the input symbol via domain policy (trim + uppercase).
- Delegates directly to the adapter's `get_bars`.
- Does NOT sort, dedupe, cache, or reshape data.

Assumptions (per MarketData port contract):
- Adapters return `list[Bar]` in chronological order (oldest → newest).
- Prices are Decimal; timestamps are UTC datetime.

Errors:
- Surfaces MarketDataError as-is from the adapter.
- Raises DomainPolicyError if symbol normalization results in empty value.
"""

from __future__ import annotations

from typing import List

from core.domain.models import Bar, Timeframe
from core.domain.policies import normalize_symbol, DomainPolicyError
from core.ports.market_data import MarketData, MarketDataError





class MarketDataService:
    """Façade around a MarketData port implementation."""

    def __init__(self, market_data: MarketData) -> None:
        self._md = market_data

    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100) -> List[Bar]:
        """
        Return the most recent `limit` bars for `symbol` at `timeframe`.

        Notes:
            - Input symbol is normalized via domain policy.
            - No additional processing is performed by this service.
        """
        norm_symbol = normalize_symbol(symbol)
        # Delegate directly to the adapter; allow adapter errors to surface.
        return self._md.get_bars(norm_symbol, timeframe, limit)