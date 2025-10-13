###
# Last edit: 10/5/2025
#
# Desc: Tests the get latest bars functionality
###

from core.usecases.get_latest_bars import get_latest_bars
from core.domain.models import Bar, Timeframe

class FakeMarketData:
    def get_bars(self, symbol, timeframe, limit=100):
        # Return a single deterministic bar for smoke testing
        return [Bar("1970-01-01T00:00:00Z", 1, 2, 0.5, 1.5, 123)]

    def stream_trades(self, symbol, on_trade):
        pass

def test_get_latest_bars():
    data = FakeMarketData()
    bars = get_latest_bars(data, "AAPL", Timeframe.ONE_MIN, 1)
    assert len(bars) == 1
    assert bars[0].c == 1.5

test_get_latest_bars()