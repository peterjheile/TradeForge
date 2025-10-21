"""
core.domain.ports.broker
------------------------
Broker port interface. All concrete broker adapters (e.g., Alpaca, Tradier)
must implement this protocol. The port exposes a minimal, broker-agnostic API
for placing/canceling orders and retrieving account/position state.

Adapters should surface transport/auth/policy failures by raising `BrokerError`.
"""

###
# EDITS:
# 10/5/2025: made basic interface
# 10/13/2025: Added return types for generic domain position and account
###


from __future__ import annotations

from typing import Protocol, runtime_checkable

from core.domain.models import OrderRequest, Order, Position, Account


class BrokerError(RuntimeError):
    """Raised for broker/transport/auth failures or policy rejections surfaced by adapters."""


@runtime_checkable
class Broker(Protocol):
    """Overarching abstraction all brokerage adapters must implement."""

    def place_order(self, order_req: OrderRequest) -> Order:
        """Submit a new order and return the broker's current view of it.

        May raise:
            BrokerError: On connectivity/auth issues or broker-policy rejection.
        """
        ...

    def cancel_order(self, order_id: str) -> bool:
        """Attempt to cancel an order.

        Returns:
            bool: True if the order was canceled; False if not canceled
                  (e.g., already filled, already canceled, or not found).

        May raise:
            BrokerError: On connectivity/auth issues.
        """
        ...

    def get_order(self, order_id: str) -> Order | None:
        """Fetch a single order by ID.

        Returns:
            Order | None: The order if found; None if not found.

        May raise:
            BrokerError: On connectivity/auth issues.
        """
        ...

    def get_positions(self) -> list[Position]:
        """Return current open positions in canonical shape.

        May raise:
            BrokerError: On connectivity/auth issues.
        """
        ...

    def get_account(self) -> Account:
        """Return a minimal account snapshot in canonical shape.

        May raise:
            BrokerError: On connectivity/auth issues.
        """
        ...
    