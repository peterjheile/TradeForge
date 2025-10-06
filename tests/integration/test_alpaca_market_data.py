###
# Last edit: 10/5/2025
#
# Desc: Tests the alpaca adapter
###

import os
import pytest
from dotenv import load_dotenv

from core.domain.models import Timeframe
from adapters.alpaca.market_data import AlpacaMarketData


load_dotenv() 
HAS_KEYS = bool(os.getenv("APCA_API_KEY_ID") and os.getenv("APCA_API_SECRET_KEY"))



@pytest.mark.skipif(not HAS_KEYS, reason="Set APCA_API_KEY_ID and APCA_API_SECRET_KEY to run this test")
def test_can_fetch_bars_from_alpaca():
    data = AlpacaMarketData(
        key=os.environ["APCA_API_KEY_ID"],
        secret=os.environ["APCA_API_SECRET_KEY"],
    )
    bars = data.get_bars("AAPL", Timeframe.ONE_MIN, limit=5)
    assert isinstance(bars, list)
    if bars:  # sometimes there may be no intraday bars depending on time/day
        b = bars[0]
        assert hasattr(b, "o") and hasattr(b, "c")