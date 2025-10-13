###
# EDITS:
# 10/13/2025: added normalization to an Order Request and error handling for when normalization cannot be applied correcly
# 10/13/2025: added normalization to a domain position and domain account 
###


"""
Domain-level policies: normalization that is broker-agnostic.

- No risk sizing or user caps here (those are user- or strategy-defined).
- No broker/venue constraints here (those live in broker policies).
"""



from __future__ import annotations
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


from .models import OrderRequest, Position, Account, AssetClass




class DomainPolicyError(ValueError):
    """Raised when domain normalization cannot be applied cleanly."""



def _q(val: Optional[Decimal], places: int) -> Optional[Decimal]:
    """Quantize a Decimal to the given number of places using HALF_UP."""

    if val is None: return None

    exp = Decimal((0, (1,), -places)) #10^-places e.g. places = 6 -> Decimal(0.000001)
    return val.quantize(exp, rounding=ROUND_HALF_UP)


def _norm_symbol(symbol: str, *, strip_symbol: bool = True, symbol_upper: bool = True) -> str:
    s = symbol.strip() if strip_symbol else symbol
    return s.upper() if symbol_upper else s


def _canon_asset_class(val: str | AssetClass) -> AssetClass:
    if isinstance(val, AssetClass):
        return val
    s = (val or "").strip().lower()
    for cls in AssetClass:
        if s == cls.value:
            return cls
    return AssetClass.EQUITY





def normalize_order_request(
    order: OrderRequest,
    *,
    symbol_upper: bool = True,
    strip_symbol: bool = True,
    qty_places: int = 6,
    price_places: int = 6,
    percent_places: int = 4,
) -> OrderRequest:
    """
    Return a normalized copy of `order` with:
      - symbol trimmed/uppercased (if configured),
      - qty, notional, price fields, and trail_percent quantized to stable precision.

    Notes:
      - Precision here is *broker-agnostic*. Broker tick/step enforcement should be handled
        by broker policies. This normalization just prevents pathological precision.
      - This function assumes `order` already passed dataclass __post_init__ invariants.
    """
    symbol = order.symbol
    if strip_symbol:
        symbol = symbol.strip()
    if symbol_upper:
        symbol = symbol.upper()
    if not symbol:
        raise DomainPolicyError("symbol cannot be empty after normalization")

    return replace(
        order,
        symbol=symbol,
        qty=_q(order.qty, qty_places),
        notional=_q(order.notional, price_places),
        limit_price=_q(order.limit_price, price_places),
        stop_price=_q(order.stop_price, price_places),
        trail_price=_q(order.trail_price, price_places),
        trail_percent=_q(order.trail_percent, percent_places),
    )




def normalize_position(
    position: Position,
    *,
    qty_places: int = 6,
    price_places: int = 6,
) -> Position:
    """Return a normalized copy of Position."""
    return replace(
        position,
        symbol=_norm_symbol(position.symbol),
        asset_class=_canon_asset_class(position.asset_class),
        qty=_q(position.qty, qty_places),
        avg_price=_q(position.avg_price, price_places),
        market_value=_q(position.market_value, price_places),
        unrealized_pl=_q(position.unrealized_pl, price_places),
    )


def normalize_account(
    account: Account,
    *,
    money_places: int = 6,
) -> Account:
    """Return a normalized copy of Account."""
    account_id = (account.account_id or "").strip()
    if not account_id:
        raise DomainPolicyError("account_id cannot be empty after normalization")
    currency = (account.currency or "").strip().upper()
    if not currency:
        raise DomainPolicyError("currency cannot be empty after normalization")

    return replace(
        account,
        account_id=account_id,
        currency=currency,
        cash=_q(account.cash, money_places),
        equity=_q(account.equity, money_places),
        buying_power=_q(account.buying_power, money_places),
    )