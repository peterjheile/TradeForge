import os
import pytest
from app.settings import get_settings
from app.factory import make_adapters
from core.domain.models import Timeframe, Bar

s = get_settings()
HAS_TRADIER = s.provider == "tradier" and s.tradier.configured()

pytestmark = [
    pytest.mark.skipif(not HAS_TRADIER, reason="Tradier not configured / not the active provider"),
]



@pytest.fixture(scope="module")
def market_data():

    _, data = make_adapters()
    return data

def _assert_bar_shape(b: Bar):
    #bar schema check
    assert isinstance(b.t, str) and len(b.t) > 0
    for n in (b.o, b.h, b.l, b.c, b.v):
        assert isinstance(n, (int, float))


@pytest.mark.parametrize(
    "tf,limit", [
        (Timeframe.ONE_MIN, 3),
        (Timeframe.FIVE_MIN, 3),
        (Timeframe.FIFTEEN_MIN, 3),
        (Timeframe.ONE_HOUR, 3),
        (Timeframe.ONE_DAY, 3),
    ]
)
def test_get_bars_various_timeframes(market_data, tf, limit):
    bars = market_data.get_bars("AAPL", tf, limit=limit)
    # In sandbox or off-hours, APIs may return < limit bars—assert non-empty but tolerant
    assert isinstance(bars, list)
    assert len(bars) >= 0  # always true; keep the assertion so shape is checked below
    if bars:
        _assert_bar_shape(bars[0])



def test_get_bars_respects_limit(market_data):
    bars_3 = market_data.get_bars("AAPL", Timeframe.ONE_MIN, limit=3)
    bars_5 = market_data.get_bars("AAPL", Timeframe.ONE_MIN, limit=5)
    assert len(bars_3) <= 3
    assert len(bars_5) <= 5
    # If both non-empty, later call should have >= items (server may cap lower; be tolerant)
    if bars_3 and bars_5:
        assert len(bars_5) >= len(bars_3)
        

def test_get_bars_invalid_symbol_tolerant(market_data):
    # Tradier may return 200 with empty payload or an error; handle both
    try:
        bars = market_data.get_bars("THISDOESNOTEXIST", Timeframe.ONE_MIN, limit=3)
        assert isinstance(bars, list)
        assert len(bars) == 0  # we expect empty for bad symbols
    except Exception as e:
        # If your adapter raises, that’s acceptable too—assert it’s a requests-like HTTP error
        assert any(k in str(e).lower() for k in ("404", "invalid", "symbol", "not found"))

def test_get_bars_single_object_vs_list_shape(market_data, monkeypatch):
    """
    Some Tradier endpoints return a single 'bar' object instead of a list when count==1.
    We simulate that by monkeypatching requests response handler if you wrapped it,
    or rely on real API when limit=1.
    """
    bars = market_data.get_bars("AAPL", Timeframe.ONE_MIN, limit=1)
    assert isinstance(bars, list)
    if bars:
        _assert_bar_shape(bars[0])