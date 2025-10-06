###
# Last edit: 10/5/2025
#
# Desc: Overarching Abstraction interface that all connected brokerage accounts link through.
###


from typing import Protocol, Any
from core.domain.models import OrderRequest, Order

class Broker(Protocol):

    #submit a new order, return order submitted
    def place_order(self, order_req: OrderRequest) -> Order:
        pass

    #cancel an order, return True/False if canceled successfully or not
    def cancel_order(self, order_id: str) -> bool:
        pass

    #requesst curretn positions, return list of current positions
    def get_position(self) -> list[dict[str, Any]]:
        pass

    #request account information, return basic information about account (equity, cash, etc)
    def get_account(self) -> dict[str, Any]:
        pass

    