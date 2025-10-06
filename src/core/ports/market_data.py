###
# Last edit: 10/5/2025
#
# Desc: Overarching Abstraction interface that market data from brokers feeds through
###


from typing import Protocol, Callable, List
from core.domain.models import Bar, Timeframe


class MarketData(Protocol):

    #pass in timeframe, symbol and return a list of bars/data from the most recent n (limit) of that timeframe
    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int=100) -> List[Bar]:
        pass

    #in case of live trading, calling ontrade for each tick
    def stream_trades(self, symbol: str, on_trade: Callable[[dict], None]) -> None:
        pass