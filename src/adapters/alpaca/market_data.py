###
# Last edit: 10/5/2025
#
# Desc: alpaca specific marketdata class inheriting from marketdata interface
###

from __future__ import annotations
from typing import List
from datetime import datetime, timedelta, timezone

from core.domain.models import Bar, Timeframe
from core.ports.market_data import MarketData
from .mappers import map_timeframe

#lazy import so that my project will still install even if alpaca-py is not present
try:
    from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
except Exception as e:  # pragma: no cover
    StockHistoricalDataClient = None
    CryptoHistoricalDataClient = None
    StockBarsRequest = None
    CryptoBarsRequest = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None



#alpaca implementation of marketdata port, historical bars only for now
class AlpacaMarketData(MarketData):

    def __init__(self, key: str, secret: str):
        if _IMPORT_ERROR:
            raise RuntimeError(
                "alpaca-py is required for AlpakaMarketData. "
                "Instqall with: pip install alpaca-py"
            ) from _IMPORT_ERROR
        
        self._stock = StockHistoricalDataClient(key, secret)
        self._crypto = CryptoHistoricalDataClient(key, secret)


    #quick heuristic to see if the symbol is a cryptocurrent
    #NOTE; NOT ALWAYS RIGHT BUT WORKS FOR NOW
    def _is_crypto(self, symbol: str) -> bool:
        return "/" in symbol


    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int=100) -> List[Bar]:
        alpaca_tf = map_timeframe(timeframe)

        end = datetime.now(timezone.utc)
        start = end - timedelta(days=7)

        if self._is_crypto(symbol):
            req = CryptoBarsRequest(
                symbol_or_symbols=symbol,
                timeframe = alpaca_tf,
                start = start,
                end = end,
                limit = limit,
                feed = "iex"
            )
            resp = self._crypto.get_crypto_bars(req)
            bars = resp.data.get(symbol, [])
        else:
            req = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe = alpaca_tf,
                start = start,
                end = end,
                limit = limit,
                feed = "iex"
            )
            resp = self._stock.get_stock_bars(req)
            bars = resp.data.get(symbol, [])

        
        #return list of Bar
        return [
            Bar(
                t=b.timestamp.isoformat(),
                o = b.open,
                h = b.high,
                l = b.low,
                c = b.close,
                v = b.volume
            ) for b in bars
        ]
    

    def stream_trades(self, symbol: str, on_trade):
        raise NotImplementedError("Live Streaming not implemented yet.")
