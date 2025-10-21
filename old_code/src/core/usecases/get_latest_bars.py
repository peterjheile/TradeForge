###
# Last edit: 10/5/2025
#
# Desc: entrypoint to fetch recent bars
###

from typing import List
from core.domain.models import Bar, Timeframe
from core.ports.market_data import MarketData

def get_latest_bars(data: MarketData, symbol: str, timeframe: Timeframe, limit: int = 100) -> List[Bar]:
    return data.get_bars(symbol=symbol, timeframe=timeframe, limit=limit)