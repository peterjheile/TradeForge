import types
import pytest

# Import the module under test so we can monkeypatch its TradingClient and APIError
import adapters.alpaca.broker as broker_mod

from core.domain.models import (
    OrderRequest, Side, OrderType, TimeInForce, OrderStatus
)
from app.settings import AlpacaSettings  # adjust path if different

# ------- Fakes (no HTTP) -------

class FakeOrder:
    def __init__(self, symbol="AAPL", status="accepted", filled_qty="0"):
        self.id = "ord_123"
        self.symbol = symbol
        self.status = status
        self.filled_qty = filled_qty

class FakeTradingClient:
    """Captures the last order request object and returns a fake order."""
    def __init__(self, key, secret, paper=True):
        self.key, self.secret, self.paper = key, secret, paper
        self.last_request = None
        self.raise_api_error = False
        self.api_error_message = "broker said no"

    def submit_order(self, order_req):
        self.last_request = order_req
        if self.raise_api_error:
            # Raise whatever the adapter is catching as APIError
            raise broker_mod.APIError(self.api_error_message)  # type: ignore
        return FakeOrder(symbol=getattr(order_req, "symbol", "AAPL"))

@pytest.fixture(autouse=True)
def patch_trading_client(monkeypatch):
    # Patch TradingClient used inside the adapter to our fake
    monkeypatch.setattr(broker_mod, "TradingClient", FakeTradingClient)
    # Provide a stand-in APIError class in the module (so we can raise it)
    class DummyAPIError(Exception): ...
    monkeypatch.setattr(broker_mod, "APIError", DummyAPIError)
    yield

@pytest.fixture
def adapter():
    settings = AlpacaSettings(key="k", secret="s", paper=True, feed="iex")  # feed unused here
    return broker_mod.AlpacaBroker(settings)

def _last_request(adapter) -> object:
    # reach into the fake client to inspect the built request object type/fields
    return adapter._client.last_request  # type: ignore[attr-defined]

# ------- Positive cases -------

def test_place_market_builds_market_request(adapter):
    req = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
    order = adapter.place_order(req)
    lr = _last_request(adapter)
    # Ensure correct Alpaca request type was built
    from alpaca.trading.requests import MarketOrderRequest
    assert isinstance(lr, MarketOrderRequest)
    assert order.symbol == "AAPL"
    assert order.status in {
        OrderStatus.ACCEPTED, OrderStatus.NEW, OrderStatus.PENDING_NEW,
        OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED, OrderStatus.DONE_FOR_DAY,
        OrderStatus.CALCULATED,
    }

def test_place_limit_requires_limit_price_and_builds_limit(adapter):
    # Missing limit_price -> error
    bad = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.LIMIT, time_in_force=TimeInForce.DAY)
    with pytest.raises(broker_mod.BrokerOrderError) as e:
        adapter.place_order(bad)
    assert "limit_price" in str(e.value).lower()

    # With price -> success and correct request type
    ok = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.LIMIT,
                      time_in_force=TimeInForce.DAY, limit_price=10.0)
    order = adapter.place_order(ok)
    from alpaca.trading.requests import LimitOrderRequest
    assert isinstance(_last_request(adapter), LimitOrderRequest)
    assert order.symbol == "AAPL"

def test_place_stop_requires_stop_price_and_builds_stop(adapter):
    bad = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.STOP, time_in_force=TimeInForce.DAY)
    with pytest.raises(broker_mod.BrokerOrderError) as e:
        adapter.place_order(bad)
    assert "stop_price" in str(e.value).lower()

    ok = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.STOP,
                      time_in_force=TimeInForce.DAY, stop_price=9.5)
    order = adapter.place_order(ok)
    from alpaca.trading.requests import StopOrderRequest
    assert isinstance(_last_request(adapter), StopOrderRequest)
    assert order.symbol == "AAPL"

def test_place_stop_limit_requires_both_prices(adapter):
    # Missing stop_price
    bad1 = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.STOP_LIMIT,
                        time_in_force=TimeInForce.DAY, limit_price=10.0)
    with pytest.raises(broker_mod.BrokerOrderError) as e1:
        adapter.place_order(bad1)
    assert "stop_price" in str(e1.value).lower()

    # Missing limit_price
    bad2 = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.STOP_LIMIT,
                        time_in_force=TimeInForce.DAY, stop_price=10.5)
    with pytest.raises(broker_mod.BrokerOrderError) as e2:
        adapter.place_order(bad2)
    assert "limit_price" in str(e2.value).lower()

    # Both supplied -> builds StopLimitOrderRequest
    ok = OrderRequest(symbol="AAPL", qty=1, side=Side.BUY, type=OrderType.STOP_LIMIT,
                      time_in_force=TimeInForce.DAY, stop_price=10.5, limit_price=10.0)
    order = adapter.place_order(ok)
    from alpaca.trading.requests import StopLimitOrderRequest
    assert isinstance(_last_request(adapter), StopLimitOrderRequest)
    assert order.symbol == "AAPL"

def test_trailing_stop_requires_exactly_one_trailing_param(adapter):
    # Neither -> error
    bad0 = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.TRAILING_STOP,
                        time_in_force=TimeInForce.DAY)
    with pytest.raises(broker_mod.BrokerOrderError) as e0:
        adapter.place_order(bad0)
    msg0 = str(e0.value).lower()
    assert "trailing stop requires exactly one" in msg0

    # Both -> error
    bad2 = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.TRAILING_STOP,
                        time_in_force=TimeInForce.DAY, trail_price=0.5, trail_percent=1.0)
    with pytest.raises(broker_mod.BrokerOrderError) as e2:
        adapter.place_order(bad2)
    msg2 = str(e2.value).lower()
    assert "exactly one" in msg2

    # Only trail_price -> OK
    ok_price = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.TRAILING_STOP,
                            time_in_force=TimeInForce.DAY, trail_price=0.5)
    order1 = adapter.place_order(ok_price)
    from alpaca.trading.requests import TrailingStopOrderRequest
    assert isinstance(_last_request(adapter), TrailingStopOrderRequest)
    assert order1.symbol == "AAPL"

    # Only trail_percent -> OK
    ok_pct = OrderRequest(symbol="AAPL", qty=1, side=Side.SELL, type=OrderType.TRAILING_STOP,
                          time_in_force=TimeInForce.DAY, trail_percent=1.0)
    order2 = adapter.place_order(ok_pct)
    assert isinstance(_last_request(adapter), TrailingStopOrderRequest)
    assert order2.symbol == "AAPL"

# ------- Negative/error paths -------

def test_mapper_failure_is_wrapped(adapter, monkeypatch):
    # Force map_order_type to blow up to test your wrapper error
    def bad_map(_):
        raise ValueError("nope")
    monkeypatch.setattr(broker_mod, "map_order_type", bad_map)
    with pytest.raises(broker_mod.BrokerOrderError) as e:
        adapter.place_order(OrderRequest(symbol="AAPL", qty=1, side=Side.BUY,
                                         type=OrderType.MARKET, time_in_force=TimeInForce.DAY))
    assert "failed to build order request" in str(e.value).lower()

def test_api_error_is_wrapped(adapter, monkeypatch):
    # Make the fake client raise the APIError class the adapter is catching
    adapter._client.raise_api_error = True  # type: ignore[attr-defined]
    with pytest.raises(broker_mod.BrokerOrderError) as e:
        adapter.place_order(OrderRequest(symbol="AAPL", qty=1, side=Side.BUY,
                                         type=OrderType.MARKET, time_in_force=TimeInForce.DAY))
    assert "alpaca rejected" in str(e.value).lower()