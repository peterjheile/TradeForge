import pytest

from app.providers.base import register, get_provider, _REGISTRY
from core.ports.broker import Broker
from core.ports.market_data import MarketData

# --- Fakes (no network)
class FakeBroker(Broker):
    def place_order(self, req): return type("Order", (), {"id": "1", "symbol": "AAPL", "status": "accepted", "filled_qty": 0.0})
    def cancel_order(self, order_id): pass
    def get_positions(self): return []
    def get_account(self): return {"cash": "10000"}

class FakeMarketData(MarketData):
    def get_bars(self, symbol, timeframe, limit=100):
        Bar = type("Bar", (), {})
        return [Bar()]  # we don't care about fields here
    def stream_trades(self, symbol, on_trade): pass

# --- Fake provider
class _FakeProvider:
    name = "fake"
    def build(self, settings):
        return FakeBroker(), FakeMarketData()
    

@pytest.fixture(autouse=True)
def clean_registry():
    # isolate registry state per test
    orig = dict(_REGISTRY)
    _REGISTRY.clear()
    try:
        yield
    finally:
        _REGISTRY.clear()
        _REGISTRY.update(orig)


def test_register_and_resolve_provider():
    register(_FakeProvider())
    p = get_provider("fake")
    assert p.name == "fake"
    broker, data = p.build(settings=None)
    assert isinstance(broker, FakeBroker)
    assert isinstance(data, FakeMarketData)


def test_unknown_provider_errors():
    with pytest.raises(ValueError) as e:
        get_provider("does-not-exist")
    assert "Unknown provider" in str(e.value)



def test_duplicate_registration_errors():
    register(_FakeProvider())
    with pytest.raises(ValueError) as e:
        register(_FakeProvider())
    assert "already registered" in str(e.value)