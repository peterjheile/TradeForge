###
# EDITS:
# Desc: 
# 10/6/2025: created file and made super basic place_order, cancel_order, get_positions, and get_account
# 10/8/2025: Createed advanced place_order function to allow for all alpaca api orders to be utilized
# 10/13/2025: Added simple preflight check for alpacabroker
###

from __future__ import annotations
from typing import Optional
from decimal import Decimal

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import (
    MarketOrderRequest,
    LimitOrderRequest,
    StopOrderRequest,
    StopLimitOrderRequest,
    TrailingStopOrderRequest,
)

from alpaca.trading.enums import OrderType as AlpacaOT


from alpaca.common.exceptions import APIError
from core.domain.models import Order, OrderRequest, OrderStatus, Side
from adapters.alpaca.mappers import (
    map_time_in_force, map_side, map_order_type,
)
from core.ports.broker import Broker
from app.settings import AlpacaSettings
from functools import lru_cache


class BrokerOrderError(RuntimeError):
     """User-facing broker (i.e alpaca) error with a clean message."""


#return the string message to be added for a given api error
def _APIError_addentum(e: APIError) -> str:
    msg = str(e)
    lower = msg.lower()
    if "wash trade" in lower:
        msg += "  Hint: wait for previous order to fill or cancel opposite open orders."
    elif "insufficient balance" in lower or "buying power" in lower:
        msg += "  Hint: lower the order size or check available buying power."
    elif "unauthorized" in lower:
        msg += ("  Hint: verify your API key/secret, paper/live flag, and IP allowlist "
                "in the Alpaca dashboard.")
    elif "forbidden" in lower or "403" in lower:
        msg += "  Hint: ensure the account is approved for this instrument type."

    return msg



def _require(name: str, value: Optional[float | Decimal]) -> float | Decimal:
    if value is None:
        raise BrokerOrderError(f"Missing required parameter '{name}' for this order type.")
    return value




class AlpacaBroker(Broker):

    def __init__(self, alpaca: AlpacaSettings):
        self._client = TradingClient(alpaca.key, alpaca.secret, paper=alpaca.paper)



    @lru_cache(maxsize=1)
    def _preflight(self):
        acct = self._client.get_account()

        if not self._client.paper and getattr(acct, "status", "").upper() != "ACTIVE":
            raise BrokerOrderError(f"Account not ACTIVE (status={acct.status}).")
        if getattr(acct, "trading_blocked", False):
            raise BrokerOrderError("Trading is blocked on this account.")
        
        #pk/ak sanity checks
        key = getattr(self._client, "_key_id", "")
        if self._client.paper and not str(key).startswith("PK"):
            raise BrokerOrderError("Paper trading enabled but key doesn’t look like a paper key (PK...).")
        if not self._client.paper and not str(key).startswith("AK"):
            raise BrokerOrderError("Live trading enabled but key doesn’t look like a live key (AK...).")


    def place_order(self, req: OrderRequest) -> Order:
        self._preflight()


        try:
            tif = map_time_in_force(req.time_in_force)
            side = map_side(req.side)
            ot = map_order_type(req.type)

            
            match ot:
                case AlpacaOT.MARKET:
                    order_req = MarketOrderRequest(
                        symbol=req.symbol,
                        qty=req.qty,
                        side=side,
                        time_in_force=tif,
                    )
                case AlpacaOT.LIMIT:
                    order_req = LimitOrderRequest(
                        symbol=req.symbol,
                        qty=req.qty,
                        side=side,
                        time_in_force=tif,
                        limit_price=_require("limit_price", req.limit_price),
                    )
                case AlpacaOT.STOP:
                    order_req = StopOrderRequest(
                        symbol=req.symbol,
                        qty=req.qty,
                        side=side,
                        time_in_force=tif,
                        stop_price=_require("stop_price", req.stop_price),
                    )
                case AlpacaOT.STOP_LIMIT:
                    order_req = StopLimitOrderRequest(
                        symbol=req.symbol,
                        qty=req.qty,
                        side=side,
                        time_in_force=tif,
                        stop_price= _require("stop_price", req.stop_price),
                        limit_price= _require("limit_price", req.limit_price),
                    )
                case AlpacaOT.TRAILING_STOP:
                    has_tp = req.trail_price is not None
                    has_pct = req.trail_percent is not None
                    if has_tp == has_pct:
                        raise BrokerOrderError(
                            "Trailing stop requires exactly one of 'trail_price' or 'trail_percent'."
                        )
                    order_req = TrailingStopOrderRequest(
                        symbol=req.symbol,
                        qty=req.qty,
                        side=side,
                        time_in_force=tif,
                        trail_price=req.trail_price,
                        trail_percent=req.trail_percent,
                    )
                case _:
                    #raise an error
                    raise BrokerOrderError(f"Unsupported order type: {ot}")
        
        except BrokerOrderError:
            # raise own Broker Error Defined
            raise
        except Exception as e:
            #raise any unewxpected clinet side error
            raise BrokerOrderError(f"Failed to build order request: {e}") from e



        #submit order to alpca
        try: 
            alpaca_order = self._client.submit_order(order_req)
        except APIError as e:
            msg = _APIError_addentum(e)
            raise BrokerOrderError(f"Alpaca rejected the order: {msg}") from e



        filled = alpaca_order.filled_qty
        try:
            filled_f = float(filled or 0.0)
        except Exception:
            filled_f = 0.0


        return Order(
            id = alpaca_order.id,
            symbol = alpaca_order.symbol,
            status = OrderStatus(alpaca_order.status),
            filled_qty=filled_f
        )
    #NOTE: THERE ARE SOME ORDER VALUES THAT I HAVE NOT ADDED



    #cancel and order by a given id
    def cancel_order(self, order_id: str) -> None:
        self._client.cancel_order_by_id(order_id)


    #get all of the current positions with an account (remember that each broker can have multiple accounts though)
    def get_positions(self) -> list[dict]:
        return [p.__dict__ for p in self._client.get_all_positions()]
    

    #get the account, just returns a dict describing the account
    def get_account(self) -> dict:
        return self._client.get_account().__dict__





