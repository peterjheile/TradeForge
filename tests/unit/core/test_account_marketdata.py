"""
Comprehensive tests for GenericAccount.get_bars using MarketDataService.
Covers delegation, symbol normalization, chronological ordering, de-duplication,
and cache hit/expiry behavior.
"""

from decimal import Decimal
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from core.services.account import GenericAccount
from core.services.market_data import MarketDataService
from core.domain.models import Bar, Timeframe


# ----------------------------
# Helpers
# ----------------------------
def _d(x) -> Decimal:
    return Decimal(str(x))


def _t(yyyy, mm, dd, hh=0, mi=0, ss=0) -> datetime:
    return datetime(yyyy, mm, dd, hh, mi, ss)


# ----------------------------
# Tests
# ----------------------------

def test_account_get_bars_delegates_and_normalizes_ordering_and_duplicates():
    """
    Account.get_bars should funnel through MarketDataService which:
      - uppercases/strips symbol before calling the port
      - removes duplicate timestamps (keeps the last occurrence)
      - sorts bars oldest → newest
    """
    # Underlying MarketData port (mock)
    port = MagicMock(name="MockMarketDataPort")

    # Out-of-order with a duplicate timestamp (t1 appears twice; second should win)
    t0 = _t(2025, 1, 1, 9, 30)
    t1 = _t(2025, 1, 1, 9, 31)
    bars_from_port = [
        Bar(timestamp=t1, o=_d("10"), h=_d("11"), l=_d("9.9"), c=_d("10.5"), v=150),   # first t1
        Bar(timestamp=t0, o=_d("9"),  h=_d("10.5"), l=_d("8.9"), c=_d("10.0"), v=200), # t0
        Bar(timestamp=t1, o=_d("10.1"), h=_d("11.1"), l=_d("9.95"), c=_d("10.6"), v=175), # second t1 (should win)
    ]
    port.get_bars.return_value = bars_from_port

    # Real service wrapping the mock port (enable cache so we can test a hit)
    mds = MarketDataService(port, cache_ttl=60.0, max_cache_entries=16)

    # Account uses the service
    acct = GenericAccount(broker=MagicMock(), data_service=mds)

    # Note symbol has whitespace + lower; service should pass "AAPL" to port
    result = acct.get_bars("  aapl  ", Timeframe.ONE_MIN, 3)

    # Verify the port was called with normalized symbol and same params
    port.get_bars.assert_called_once_with("AAPL", Timeframe.ONE_MIN, 3)

    # Result should be deduped (2 bars) and ordered (t0, t1)
    assert [b.timestamp for b in result] == [t0, t1]
    # For duplicate t1, the LAST occurrence from the port should be kept (c=10.6, v=175)
    assert result[-1].c == _d("10.6")
    assert result[-1].v == 175

    # Second call should hit cache → port still called only once
    result2 = acct.get_bars("aapl", Timeframe.ONE_MIN, 3)
    assert result2 is result  # same list object from cache
    port.get_bars.assert_called_once()  # no extra call


def test_cache_expiry_triggers_refetch(monkeypatch):
    """
    When TTL expires, the MarketDataService should refetch from the port.
    Use a fake monotonic clock to simulate time passing.
    """
    port = MagicMock(name="MockMarketDataPort")

    t0 = _t(2025, 1, 1, 9, 30)
    bars_first = [Bar(timestamp=t0, o=_d("1"), h=_d("1"), l=_d("1"), c=_d("1"), v=1)]
    bars_second = [Bar(timestamp=t0, o=_d("2"), h=_d("2"), l=_d("2"), c=_d("2"), v=2)]

    # First call returns bars_first; after expiry, return bars_second
    port.get_bars.side_effect = [bars_first, bars_second]

    # Fake monotonic clock
    class _Clock:
        def __init__(self):
            self.now = 1000.0

        def __call__(self):
            return self.now

    clock = _Clock()
    monkeypatch.setattr("core.services.market_data.monotonic", clock)

    # TTL = 10 sec
    mds = MarketDataService(port, cache_ttl=10.0, max_cache_entries=16)
    acct = GenericAccount(broker=MagicMock(), data_service=mds)

    # First fetch → port called (cached)
    res1 = acct.get_bars("AAPL", Timeframe.ONE_MIN, 1)
    assert res1[0].o == _d("1")
    assert port.get_bars.call_count == 1

    # Within TTL → cache hit (no extra call)
    clock.now += 5.0
    res2 = acct.get_bars("AAPL", Timeframe.ONE_MIN, 1)
    assert res2 is res1
    assert port.get_bars.call_count == 1

    # After TTL → refetch
    clock.now += 10.1
    res3 = acct.get_bars("AAPL", Timeframe.ONE_MIN, 1)
    assert res3[0].o == _d("2")
    assert port.get_bars.call_count == 2


def test_cache_key_includes_symbol_timeframe_and_limit():
    """
    Ensure different (symbol, timeframe, limit) combos are cached independently.
    """
    port = MagicMock(name="MockMarketDataPort")
    t = _t(2025, 1, 1, 9, 30)
    port.get_bars.return_value = [Bar(timestamp=t, o=_d("1"), h=_d("1"), l=_d("1"), c=_d("1"), v=1)]

    mds = MarketDataService(port, cache_ttl=60.0, max_cache_entries=16)
    acct = GenericAccount(broker=MagicMock(), data_service=mds)

    acct.get_bars("AAPL", Timeframe.ONE_MIN, 10)   # call 1
    acct.get_bars("AAPL", Timeframe.FIVE_MIN, 10)  # call 2
    acct.get_bars("MSFT", Timeframe.ONE_MIN, 10)   # call 3
    acct.get_bars("AAPL", Timeframe.ONE_MIN, 20)   # call 4

    # All are different cache keys → 4 calls to the underlying port
    assert port.get_bars.call_count == 4