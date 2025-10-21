
###
# EDITS:
# 10/13/2025: Created Comprehensive test of Domain Enumerations and Models
###



import pytest
from decimal import Decimal
from datetime import datetime
from dataclasses import FrozenInstanceError

from core.domain.models import (
    OrderRequest, Order, Bar,
    Side, OrderType, TimeInForce, AssetClass, OrderStatus
)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _d(x) -> Decimal:
    return Decimal(str(x))

def _mk_market_qty(**overrides) -> OrderRequest:
    base = dict(
        symbol="AAPL",
        side=Side.BUY,
        type=OrderType.MARKET,
        qty=_d("1.25"),
        notional=None,
    )
    base.update(overrides)
    return OrderRequest(**base)

def _mk_market_notional(**overrides) -> OrderRequest:
    base = dict(
        symbol="AAPL",
        side=Side.BUY,
        type=OrderType.MARKET,
        qty=None,
        notional=_d("50"),
    )
    base.update(overrides)
    return OrderRequest(**base)

# -------------------------------------------------------------------
# Happy paths
# -------------------------------------------------------------------

def test_market_qty_ok_defaults():
    o = _mk_market_qty()
    assert o.time_in_force == TimeInForce.DAY
    assert o.asset_class == AssetClass.EQUITY
    assert o.notional is None and o.qty == _d("1.25")

def test_market_notional_ok_defaults():
    o = _mk_market_notional()
    assert o.qty is None and o.notional == _d("50")

def test_limit_ok():
    o = OrderRequest(
        symbol="AAPL", side=Side.BUY, type=OrderType.LIMIT,
        qty=_d("1"), limit_price=_d("100.00")
    )
    assert o.limit_price == _d("100.00")

def test_stop_ok():
    o = OrderRequest(
        symbol="AAPL", side=Side.SELL, type=OrderType.STOP,
        qty=_d("1"), stop_price=_d("95.00")
    )
    assert o.stop_price == _d("95.00")

def test_stop_limit_ok():
    o = OrderRequest(
        symbol="AAPL", side=Side.SELL, type=OrderType.STOP_LIMIT,
        qty=_d("1"), stop_price=_d("95.00"), limit_price=_d("94.50")
    )
    assert (o.stop_price, o.limit_price) == (_d("95.00"), _d("94.50"))

@pytest.mark.parametrize("trail_field", ["trail_price", "trail_percent"])
def test_trailing_stop_ok(trail_field):
    kwargs = dict(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP, qty=_d("1"))
    if trail_field == "trail_price":
        kwargs["trail_price"] = _d("1.00")
    else:
        kwargs["trail_percent"] = _d("1.5")
    o = OrderRequest(**kwargs)
    assert (o.trail_price, o.trail_percent) in ((_d("1.00"), None), (None, _d("1.5")))

# -------------------------------------------------------------------
# qty vs notional invariants
# -------------------------------------------------------------------

@pytest.mark.parametrize("qty,notional,msg", [
    (None, None, "Exactly one of qty or notional must be provided"),
    (_d("1"), _d("10"), "Exactly one of qty or notional must be provided"),
    (_d("0"), None, "qty must be > 0"),
    (_d("-1"), None, "qty must be > 0"),
    (None, _d("0"), "notional must be > 0"),
    (None, _d("-5"), "notional must be > 0"),
])
def test_qty_notional_invariants(qty, notional, msg):
    with pytest.raises(ValueError) as e:
        OrderRequest(symbol="AAPL", side=Side.BUY, type=OrderType.MARKET, qty=qty, notional=notional)
    assert msg in str(e.value)

# -------------------------------------------------------------------
# Order-type specific constraints
# -------------------------------------------------------------------

def test_market_rejects_all_price_trailing_fields():
    for kwargs in (
        dict(limit_price=_d("100")),
        dict(stop_price=_d("90")),
        dict(trail_price=_d("1")),
        dict(trail_percent=_d("1.5")),
    ):
        with pytest.raises(ValueError) as e:
            _mk_market_qty(**kwargs)
        assert "MARKET orders cannot include" in str(e.value)

def test_limit_requires_only_limit_price():
    # missing limit_price
    with pytest.raises(ValueError) as e:
        OrderRequest(symbol="AAPL", side=Side.BUY, type=OrderType.LIMIT, qty=_d("1"))
    assert "LIMIT orders require limit_price" in str(e.value)

    # rejects stop/trailing
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.BUY, type=OrderType.LIMIT, qty=_d("1"),
                     limit_price=_d("100"), stop_price=_d("95"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.BUY, type=OrderType.LIMIT, qty=_d("1"),
                     limit_price=_d("100"), trail_price=_d("1"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.BUY, type=OrderType.LIMIT, qty=_d("1"),
                     limit_price=_d("100"), trail_percent=_d("1.5"))

def test_stop_requires_only_stop_price():
    # missing stop_price
    with pytest.raises(ValueError) as e:
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP, qty=_d("1"))
    assert "STOP orders require stop_price" in str(e.value)

    # rejects limit/trailing
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP, qty=_d("1"),
                     stop_price=_d("95"), limit_price=_d("94"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP, qty=_d("1"),
                     stop_price=_d("95"), trail_price=_d("1"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP, qty=_d("1"),
                     stop_price=_d("95"), trail_percent=_d("1.5"))

def test_stop_limit_requires_both_and_no_trailing():
    # missing one component
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP_LIMIT, qty=_d("1"),
                     stop_price=_d("95"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP_LIMIT, qty=_d("1"),
                     limit_price=_d("94"))
    # trailing not allowed
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.STOP_LIMIT, qty=_d("1"),
                     stop_price=_d("95"), limit_price=_d("94"), trail_price=_d("1"))

def test_trailing_stop_requires_exactly_one_trailing_and_no_limit_or_stop():
    # neither trailing field
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP, qty=_d("1"))
    # both trailing fields
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP, qty=_d("1"),
                     trail_price=_d("1"), trail_percent=_d("1.5"))
    # no limit/stop allowed
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP, qty=_d("1"),
                     trail_price=_d("1"), limit_price=_d("100"))
    with pytest.raises(ValueError):
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP, qty=_d("1"),
                     trail_percent=_d("1.5"), stop_price=_d("95"))

# -------------------------------------------------------------------
# Shared numeric validations (matched to allowed order types)
# -------------------------------------------------------------------

@pytest.mark.parametrize("field,val,msg", [
    ("limit_price", _d("0"), "price fields must be > 0"),
    ("limit_price", _d("-1"), "price fields must be > 0"),
    ("stop_price",  _d("0"), "price fields must be > 0"),
    ("stop_price",  _d("-1"), "price fields must be > 0"),
    ("trail_price", _d("-0.01"), "price fields must be > 0"),
])
def test_price_fields_must_be_positive(field, val, msg):
    # Choose an order type that allows the field being tested
    matrix = {
        "limit_price": (OrderType.LIMIT, {"limit_price": _d("100")}),
        "stop_price":  (OrderType.STOP,  {"stop_price":  _d("100")}),
        "trail_price": (OrderType.TRAILING_STOP, {"trail_price": _d("1")}),
    }
    otype, base = matrix[field]
    data = dict(symbol="AAPL", side=Side.BUY, type=otype, qty=_d("1"), **base)
    data[field] = val
    with pytest.raises(ValueError) as e:
        OrderRequest(**data)
    assert msg in str(e.value)

@pytest.mark.parametrize("val", [_d("0"), _d("-1"), _d("-0.0001")])
def test_trail_percent_must_be_positive(val):
    with pytest.raises(ValueError) as e:
        OrderRequest(symbol="AAPL", side=Side.SELL, type=OrderType.TRAILING_STOP,
                     qty=_d("1"), trail_percent=val)
    assert "trail_percent must be > 0" in str(e.value)

# -------------------------------------------------------------------
# Other models: Order and Bar
# -------------------------------------------------------------------

def test_order_accepts_canonical_status_and_datetimes():
    now = datetime.utcnow()  # naive UTC in this domain
    o = Order(
        id="abc123",
        symbol="AAPL",
        status=OrderStatus.NEW,
        filled_qty=_d("0"),
        submitted_at=now,
        filled_at=None,
        client_order_id="cid-1",
        raw_status="pending_new",
        raw_payload={"broker": "alpaca"},
    )
    assert o.status == OrderStatus.NEW
    assert o.filled_at is None
    assert o.raw_status == "pending_new"

def test_bar_types_and_values():
    now = datetime.utcnow()
    b = Bar(timestamp=now, o=_d("100.00"), h=_d("101.00"), l=_d("99.50"), c=_d("100.50"), v=123456)
    assert b.c == _d("100.50")
    assert isinstance(b.v, int)

# -------------------------------------------------------------------
# Immutability (frozen dataclasses)
# -------------------------------------------------------------------

def test_order_request_is_frozen():
    o = _mk_market_qty()
    with pytest.raises(FrozenInstanceError):
        o.symbol = "MSFT"

def test_order_is_frozen():
    o = Order(id="1", symbol="AAPL", status=OrderStatus.NEW, filled_qty=_d("0"))
    with pytest.raises(FrozenInstanceError):
        o.status = OrderStatus.FILLED