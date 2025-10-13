###
# EDITS:
# 10/13/2025: Created Comprehensive test of Domain policies (i.e. the OrderRequest normalization)
###



import pytest
from decimal import Decimal
from dataclasses import FrozenInstanceError

from core.domain.models import OrderRequest, Side, OrderType, TimeInForce, AssetClass
from core.domain.policies import normalize_order_request, DomainPolicyError


# ----------------------------
# Helpers
# ----------------------------

def _d(x) -> Decimal:
    return Decimal(str(x))

def _mk_limit(**overrides) -> OrderRequest:
    base = dict(
        symbol=" aapl ",
        side=Side.BUY,
        type=OrderType.LIMIT,
        qty=_d("1.23456789"),
        limit_price=_d("100.123456789"),
        notional=None,
        time_in_force=TimeInForce.DAY,
        asset_class=AssetClass.EQUITY,
    )
    base.update(overrides)
    return OrderRequest(**base)

def _mk_stop(**overrides) -> OrderRequest:
    base = dict(
        symbol="\tmsft\n",
        side=Side.SELL,
        type=OrderType.STOP,
        qty=_d("2.0000000009"),
        stop_price=_d("95.999999999"),
        notional=None,
    )
    base.update(overrides)
    return OrderRequest(**base)

def _mk_trailing_stop(**overrides) -> OrderRequest:
    base = dict(
        symbol=" btc/usd ",
        side=Side.SELL,
        type=OrderType.TRAILING_STOP,
        qty=_d("0.123456789"),
        trail_price=_d("1.23456789"),
        trail_percent=None,
        notional=None,
    )
    base.update(overrides)
    return OrderRequest(**base)


# ----------------------------
# Symbol normalization
# ----------------------------

def test_symbol_trim_and_upper_defaults():
    o = _mk_limit()
    n = normalize_order_request(o)
    assert n.symbol == "AAPL"         # trimmed + uppercased
    assert o is not n                  # returns a new instance

def test_symbol_no_strip_no_upper_when_disabled():
    o = _mk_limit(symbol=" aapl ")
    n = normalize_order_request(o, symbol_upper=False, strip_symbol=False)
    assert n.symbol == " aapl "        # unchanged by flags

def test_symbol_becomes_empty_after_strip_raises():
    o = _mk_limit(symbol="   A   ")
    # First prove strip works:
    n = normalize_order_request(o)     # becomes "A"
    assert n.symbol == "A"
    # Now empty after strip → error
    with pytest.raises(DomainPolicyError):
        normalize_order_request(_mk_limit(symbol="   "), strip_symbol=True)


# ----------------------------
# Quantization / precision
# ----------------------------

def test_quantize_qty_and_limit_price_limit_order():
    o = _mk_limit(qty=_d("1.23456789"), limit_price=_d("100.123456789"))
    n = normalize_order_request(o, qty_places=6, price_places=6)
    assert n.qty == _d("1.234568")                # HALF_UP at 6 places
    assert n.limit_price == _d("100.123457")      # HALF_UP at 6 places
    # unchanged fields remain intact
    assert n.time_in_force == TimeInForce.DAY
    assert n.asset_class == AssetClass.EQUITY

def test_quantize_stop_price_stop_order():
    o = _mk_stop(stop_price=_d("95.999999999"))
    n = normalize_order_request(o, price_places=6)
    assert n.symbol == "MSFT"
    assert n.stop_price == _d("96.000000")

def test_quantize_trailing_fields_trailing_stop():
    o = _mk_trailing_stop(trail_price=_d("1.23456789"))
    n = normalize_order_request(o, price_places=6, percent_places=4)
    assert n.symbol == "BTC/USD"
    assert n.trail_price == _d("1.234568")
    # switch to percent and ensure 4-place rounding
    o2 = _mk_trailing_stop(trail_price=None, trail_percent=_d("1.234567"))
    n2 = normalize_order_request(o2, percent_places=4)
    assert n2.trail_percent == _d("1.2346")

def test_preserves_none_fields():
    o = _mk_limit(limit_price=_d("100.0"))
    n = normalize_order_request(o)
    assert n.notional is None
    assert n.stop_price is None
    # price remains quantized but present
    assert n.limit_price == _d("100.000000")

def test_idempotent_normalization():
    o = _mk_limit()
    n1 = normalize_order_request(o)
    n2 = normalize_order_request(n1)
    assert n1 == n2  # second pass should not change values further


# ----------------------------
# Immutability and return semantics
# ----------------------------

def test_returns_new_instance_and_stays_frozen():
    o = _mk_limit()
    n = normalize_order_request(o)
    assert o is not n
    with pytest.raises(FrozenInstanceError):
        n.symbol = "MSFT"
