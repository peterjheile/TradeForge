###
# Last edit: 10/5/2025
#
# Desc: Overarching Abstraction interface that all connected brokerage accounts link through.
###

from __future__ import annotations

from typing import Protocol, runtime_checkable, TypedDict, Optional, List
from core.domain.models import OrderRequest, Order




class BrokerError(RuntimeError):
    """Raised for broker/transport/auth failures or policy rejections surfaced by adapters."""





@runtime_checkable
class Broker(Protocol):
    """Overarching abstraction all brokerage adapters must implement."""

    def place_order(self, order_req: OrderRequest) -> Order:
        """Submit a new order and return the broker's current view of it.
        May raise BrokerError.
        """
        ...

    def cancel_order(self, order_id: str) -> bool:
        """Attempt to cancel an order. Returns True if canceled, False otherwise.
        May raise BrokerError.
        """
        ...

    def get_order(self, order_id: str) -> Optional[Order]:
        """Fetch a single order by ID (None if not found).
        May raise BrokerError.
        """
        ...

    def get_positions(self) -> List[Position]:
        """Return current open positions in canonical shape.
        May raise BrokerError.
        """
        ...

    def get_account(self) -> Account:
        """Return a minimal account snapshot in canonical shape.
        May raise BrokerError.
        """

    