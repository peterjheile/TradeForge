###
# Last edit: 10/6/2025
#
# Desc: generic account irrespecitve of provider over top of the Broker and MarketData
###

from __future__ import annotations
from typing import List
from core.ports.broker import Broker
from core.ports.market_data import MarketData
from core.domain.models import OrderRequest, Order, Side, OrderType, Timeframe, Bar, TimeInForce


class GenericAccount:

    def __init__(self, broker: Broker, data: MarketData):
        self._broker = broker
        self._data = data


    #orders
    def buy_market(self, symbol: str, qty: float,  tif: TimeInForce = TimeInForce.DAY) -> Order:
        req = OrderRequest(symbol = symbol, qty = qty,  time_in_force=tif, side = Side.BUY, type = OrderType.MARKET)
        return self._broker.place_order(req)
    

    def sell_market(self, symbol: str, qty: float, tif: TimeInForce = TimeInForce.DAY) -> Order:
        req = OrderRequest(symbol = symbol, qty = qty,  time_in_force=tif, side= Side.SELL, type=OrderType.MARKET)
        return self._broker.place_order(req)
    

    #data
    def latest_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100) -> List[Bar]:
        return self._data.get_bars(symbol, timeframe, limit)
    

    #info
    def positions(self) -> list[dict]:
        return self._broker.get_positions()
    

    def account(self) -> dict:
        return self._broker.get_account()