import pytest
from core.domain.models import Timeframe, TimeInForce, Side, OrderType
from adapters.alpaca.mappers import (
    map_timeframe, map_time_in_force, map_side, map_order_type
)

def test_map_timeframe_ok():
    assert map_timeframe(Timeframe.ONE_MIN) is not None

def test_map_timeframe_bad():
    class FakeTF: value = "2Min"
    with pytest.raises(ValueError) as e:
        map_timeframe(FakeTF)  # type: ignore
    assert "Timeframe" in str(e.value)

def test_map_tif_ok():
    assert map_time_in_force(TimeInForce.DAY).name == "DAY"

def test_map_tif_bad():
    class FakeTIF: value = "NEVER"
    with pytest.raises(ValueError) as e:
        map_time_in_force(FakeTIF)  # type: ignore
    assert "TimeInForce" in str(e.value)

def test_map_side_ok():
    assert map_side(Side.BUY).name == "BUY"

def test_map_side_bad():
    class FakeSide: value = "HOLD"
    with pytest.raises(ValueError) as e:
        map_side(FakeSide)  # type: ignore
    assert "Side" in str(e.value)

def test_map_order_type_ok():
    assert map_order_type(OrderType.TRAILING_STOP).name.lower().startswith("trailing")

def test_map_order_type_bad():
    class FakeOT: value = "iceberg"
    with pytest.raises(ValueError) as e:
        map_order_type(FakeOT)  # type: ignore
    assert "OrderType" in str(e.value)