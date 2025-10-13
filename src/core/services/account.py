"""
GenericAccount service
----------------------
Thin orchestration layer over the Broker and MarketData ports.

This version exposes a single generic `place_order` method covering all order
types, and a generic `get_bars` for historical data.
"""


###
# EDITS:
# 10/6/2025 generic account irrespecitve of provider over top of the Broker and MarketData
# 10/13/2025: further reduced function to even more generic forms now that high capability has been added to adapters.
###



from __future__ import annotations

from decimal import Decimal
from typing import Callable

from core.domain.models import (
    OrderRequest, Order, Side, OrderType, TimeInForce, Timeframe, Bar,
    Position, Account,
)
from core.domain.policies import (
    normalize_order_request, normalize_position, normalize_account,
)
from core.ports.broker import Broker
from core.ports.market_data import MarketData




class GenericAccount:
    """Broker-agnostic account facade backed by the Broker and MarketData ports."""

    def __init__(self, broker: Broker, data: MarketData):
        self._broker = broker
        self._data = data


    # --------------------
    # Orders
    # --------------------
    def place_order(
        self,
        *,
        symbol: str,
        side: Side,
        type: OrderType,
        tif: TimeInForce = TimeInForce.DAY,
        qty: Decimal | None = None,
        notional: Decimal | None = None,
        limit_price: Decimal | None = None,
        stop_price: Decimal | None = None,
        trail_price: Decimal | None = None,
        trail_percent: Decimal | None = None,
        client_order_id: str | None = None,
    ) -> Order:
        """Place an order (market, limit, stop, stop_limit, trailing_stop) using qty or notional."""
        req = OrderRequest(
            symbol=symbol,
            side=side,
            type=type,
            time_in_force=tif,
            qty=qty,
            notional=notional,
            limit_price=limit_price,
            stop_price=stop_price,
            trail_price=trail_price,
            trail_percent=trail_percent,
            client_order_id=client_order_id,
        )
        req = normalize_order_request(req)
        return self._broker.place_order(req)
    

    def cancel(self, order_id: str) -> bool:
        """Attempt to cancel an existing order. Returns True if canceled, else False."""
        return self._broker.cancel_order(order_id)

    def get_order(self, order_id: str) -> Order | None:
        """Fetch a single order by ID (None if not found)."""
        return self._broker.get_order(order_id)



    # --------------------
    # Market data (generic)
    # --------------------
    def get_bars(self, symbol: str, timeframe: Timeframe, limit: int = 100) -> list[Bar]:
        """Fetch the most recent bars (oldest → newest)."""
        return self._data.get_bars(symbol, timeframe, limit)




    # --------------------
    # Account state
    # --------------------
    def positions(self) -> list[Position]:
        """Return normalized open positions."""
        raw = self._broker.get_positions()
        return [normalize_position(p) for p in raw]

    def account(self) -> Account:
        """Return a normalized account snapshot."""
        raw = self._broker.get_account()
        return normalize_account(raw)

