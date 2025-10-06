###
# Last edit: 10/6/2025
#
# Desc: 
###

from core.domain.models import Order, OrderRequest, OrderStatus, Side
from core.ports.broker import Broker


#again lazy import so my library can install without alpaca-py isntalled
try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
except Exception as e:  # pragma: no cover
    TradingClient = None
    MarketOrderRequest = None
    LimitOrderRequest = None
    OrderSide = None
    TimeInForce = None
    _IMPORT_ERROR = e
else:
    _IMPORT_ERROR = None



#alpaca implementation of the broker port
class AlpacaBroker(Broker):

    #link to alpaca trading client, raise error if alpaca-py now installed
    def __init__(self, key: str, secret: str, paper: bool = True):
        if _IMPORT_ERROR:
            raise RuntimeError(
                "alpaca-py is required for AlpacaBroker. Install with: pip install alpaca-py"
            ) from _IMPORT_ERROR
        
        self._client = TradingClient(key, secret, paper=paper)


    #place an order, return the custom order object describing that order
    def place_order(self, req: OrderRequest) -> Order:

        if req.type.value == "market":
            order_req = MarketOrderRequest(
                symbol = req.symbol,
                qty = req.qty,
                side = OrderSide.BUY if req.side.value == "buy" else OrderSide.SELL,
                time_in_force = TimeInForce.DAY
            )
        else:
            order_req = LimitOrderRequest(
                symbol = req.symbol,
                qty = req.qty,
                side = OrderSide.BUY if req.side.value == "buy" else OrderSide.SELL,
                time_in_force = TimeInForce.Day,
                limit_price = req.limit_price
            )

        alpaca_order = self._client.submit_order(order_req)
        return Order(
            id = alpaca_order.id,
            symbol = alpaca_order.symbol,
            status = OrderStatus(alpaca_order.status),
            filled_qty = float(alpaca_order.filled_qty or 0.0)
        )
    
    
    #cancel and order by a given id
    def cancel_order(self, order_id: str) -> None:
        self._client.cancel_order_by_id(order_id)


    #get all of the current positions with an account (remember that each broker can have multiple accounts though)
    def get_positions(self) -> list[dict]:
        return [p.__dict__ for p in self._client.get_all_positions()]
    

    #get the account, just returns a dict describing the account
    def get_account(self) -> dict:
        return self._client.get_account().__dict__
    