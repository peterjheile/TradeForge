"""
Domain-level policies: normalization that is broker-agnostic.

- No risk sizing or user caps here (those are user/strategy-defined).
- No broker/venue constraints here (those live in broker adapters/policies).
- Centralizes normalization & precision for domain models, including symbols.
"""


###
# EDITS:
# 10/13/2025: added normalization to an Order Request and error handling for when normalization cannot be applied correcly
# 10/13/2025: added normalization to a domain position and domain account 
# 10/20/2025: added normalization of symbol
###


from __future__ import annotations
from dataclasses import replace
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


from .models import OrderRequest, Position, Account, AssetClass




# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------
class DomainPolicyError(ValueError):
    """Raised when domain normalization cannot be applied cleanly."""




# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _q(val: Optional[Decimal], places: int) -> Optional[Decimal]:
    """Quantize a Decimal to the given number of places using HALF_UP."""
    if val is None:
        return None
    exp = Decimal((0, (1,), -places))  # 10^-places; e.g., 6 -> Decimal('0.000001')
    return val.quantize(exp, rounding=ROUND_HALF_UP)


def normalize_symbol(symbol: str, *, strip: bool = True, upper: bool = True) -> str:
    """
    Return a normalized trading symbol.

    - Trims whitespace if `strip` is True.
    - Uppercases if `upper` is True.
    - Raises DomainPolicyError if the normalized symbol is empty.
    """
    s = symbol.strip() if strip else symbol
    s = s.upper() if upper else s
    if not s:
        raise DomainPolicyError("symbol cannot be empty after normalization")
    return s


def _canon_asset_class(val: str | AssetClass) -> AssetClass:
    """Best-effort canonicalization of asset class input."""
    if isinstance(val, AssetClass):
        return val
    s = (val or "").strip().lower()
    for cls in AssetClass:
        if s == cls.value:
            return cls
    #treat as an equity if teh asset class cannot be attributed with the val string
    return AssetClass.EQUITY






# ---------------------------------------------------------------------------
# Normalizers
# ---------------------------------------------------------------------------
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
      - symbol normalized via `normalize_symbol`,
      - qty/notional/price/trailing fields quantized to stable precision.

    Notes:
      - Precision here is *broker-agnostic*. Broker tick/step enforcement belongs
        in broker-specific policy/adapters.
      - Assumes `order` already passed dataclass __post_init__ invariants.
    """
    symbol = normalize_symbol(order.symbol, strip=strip_symbol, upper=symbol_upper)

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
        symbol=normalize_symbol(position.symbol),
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

    currency = normalize_symbol(account.currency, strip=True, upper=True)
    # currency is typically letters (e.g., USD). normalize_symbol enforces uppercase/non-empty.

    return replace(
        account,
        account_id=account_id,
        currency=currency,
        cash=_q(account.cash, money_places),
        equity=_q(account.equity, money_places),
        buying_power=_q(account.buying_power, money_places),
    )