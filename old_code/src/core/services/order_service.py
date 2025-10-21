"""
OrderService (Orchestrator)
---------------------------
Thin orchestration over the Broker port for order lifecycle operations.

Responsibilities:
- Apply broker-agnostic domain normalization (symbol, qty/notional, price fields).
- Delegate to the Broker adapter for execution and retrieval.
- Surface BrokerError/DomainPolicyError as-is.

Non-Responsibilities:
- No risk sizing or strategy logic (belongs to strategy layer).
- No broker tick/lot enforcement (belongs in broker adapters/policies).
- No retries/backoff/caching (belongs in adapters or an outer resilience layer).
"""


###
# EDITS:
# 10/20/2025: created basic orchestration functions place order, cancel order, and get order
###


from __future__ import annotations

from typing import Optional

from core.domain.models import OrderRequest, Order
from core.domain.policies import normalize_order_request, DomainPolicyError
from core.ports.broker import Broker, BrokerError




class OrderService:
    """
    Orchestrates order lifecycle by applying domain normalization
    and delegating to a concrete Broker implementation.
    """

    def __init__(self, broker: Broker) -> None:
        self._broker = broker

    # ---- Submit -------------------------------------------------------------
    def place_order(self, order_req: OrderRequest) -> Order:
        """
        Normalize and submit an order.

        Flow:
            1) Normalize (symbol upper/strip; quantize qty/prices/percent).
            2) Delegate to Broker.place_order().
            3) Return broker's canonical Order.

        Raises:
            DomainPolicyError: If normalization fails (e.g., empty symbol).
            BrokerError:       On transport/auth/broker-policy errors.
            ValueError:        If OrderRequest invariants fail (from dataclass).
        """
        normalized = normalize_order_request(order_req)
        return self._broker.place_order(normalized)

    # ---- Cancel -------------------------------------------------------------
    def cancel_order(self, order_id: str) -> bool:
        """
        Attempt to cancel an order.

        Returns:
            True if canceled; False if not canceled (e.g., already filled/not found).

        Raises:
            BrokerError: On connectivity/auth issues.
            ValueError:  If order_id is empty/blank.
        """
        oid = (order_id or "").strip()
        if not oid:
            raise ValueError("order_id cannot be empty")
        return self._broker.cancel_order(oid)

    # ---- Fetch --------------------------------------------------------------
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Fetch a single order by its ID.

        Returns:
            Order if found, otherwise None.

        Raises:
            BrokerError: On connectivity/auth issues.
            ValueError:  If order_id is empty/blank.
        """
        oid = (order_id or "").strip()
        if not oid:
            raise ValueError("order_id cannot be empty")
        return self._broker.get_order(oid)