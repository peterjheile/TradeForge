"""
MarketDataService
-----------------
Thin orchestration over the MarketData port:
- Standardizes symbol (trim + upper)
- Ensures bars are sorted oldest → newest
- Optional in-memory cache with TTL
"""


from __future__ import annotations

from collections import OrderedDict
from time import monotonic
from typing import Iterable

from core.domain.models import Bar, Timeframe
from core.ports.market_data import MarketData, MarketDataError





# -----------------
# local helpers
# -----------------

def _ensure_chronological(bars: Iterable[Bar]) -> list[Bar]:
    """Oldest → newest by bar.timestamp."""
    return sorted(bars, key=lambda b: b.timestamp)

def _dedupe_by_timestamp(bars: Iterable[Bar]) -> list[Bar]:
    """Remove duplicate bars by timestamp, keeping the last occurrence."""
    seen: dict = {}
    for b in bars:
        seen[b.timestamp] = b
    return list(seen.values())






class MarketDataService:
    """Broker-agnostic convenience wrapper around the MarketData port."""

    def __init__(self, data: MarketData, *, cache_ttl: float | None = None, max_cache_entries: int = 128):
        """
        Args:
            data: MarketData port implementation.
            cache_ttl: Seconds to keep cached results (None disables caching).
            max_cache_entries: Max cache entries (LRU).
        """
        self._data = data
        self._cache_ttl = cache_ttl
        self._cache: OrderedDict[tuple, tuple[float, list[Bar]]] = OrderedDict()
        self._max = max_cache_entries

    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100, *, use_cache: bool = True) -> list[Bar]:
        """Fetch most-recent `limit` bars for `symbol` at `timeframe`, oldest → newest."""
        sym = symbol.strip().upper()
        key = (sym, timeframe.value, int(limit))

        # cache hit
        if use_cache and self._cache_ttl is not None:
            hit = self._cache.get(key)
            if hit:
                ts, bars = hit
                if monotonic() - ts <= self._cache_ttl:
                    # move to end (LRU)
                    self._cache.move_to_end(key)
                    return bars

        # fetch from port
        bars = self._data.get_bars(sym, timeframe, limit)

        # normalize order + dedupe by timestamp (keep latest for duplicate ts)
        bars = _ensure_chronological(_dedupe_by_timestamp(bars))

        # cache store
        if use_cache and self._cache_ttl is not None:
            self._cache[key] = (monotonic(), bars)
            self._cache.move_to_end(key)
            while len(self._cache) > self._max:
                self._cache.popitem(last=False)  # evict LRU

        return bars