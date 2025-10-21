"""
core.domain.ports.market_data
-----------------------------
Market data port interface. Concrete adapters (e.g., Alpaca, Tradier) must
implement this protocol to provide historical bars.

Errors:
    Adapters should surface transport/auth/permission failures by raising
    `MarketDataError`. Implementations should normalize outputs to domain
    types (`Bar`) before returning.
"""

###
#EDITS
# 10/13/2025: Created basic overarching interface with get_bars and stream_protocols
# 10/13/2025: Added docstrean and cleaned for deployment. Removed stream_protocols as it will not be implemented for a long time
###


from __future__ import annotations

from typing import Protocol, runtime_checkable
from core.domain.models import Bar, Timeframe




class MarketDataError(RuntimeError):
    """Raised for market data transport/auth/permission failures."""




@runtime_checkable
class MarketData(Protocol):
    """Abstraction for retrieving historical market data."""

    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100) -> list[Bar]:
        """Return the most recent `limit` bars for `symbol` at `timeframe` granularity.

        Notes:
            - Bars are normalized to the domain `Bar` type (UTC timestamps, Decimal prices).
            - Implementations should return bars in **chronological order** (oldest → newest).
            - `limit` is a hint; adapters may cap or adjust it.

        Raises:
            MarketDataError: On connectivity/auth issues or unsupported timeframe.
        """
        ...