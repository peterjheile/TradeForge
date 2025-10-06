###
# Last edit: 10/6/2025
#
# Desc: Tests the alpaca broker
###

import os, pytest
from app.settings import get_settings
from adapters.alpaca.broker import AlpacaBroker
from core.domain.models import OrderRequest, Side, OrderType, OrderStatus

s = get_settings()
HAS_KEYS = bool(s.alpaca.key and s.alpaca.secret)
ALLOW_TRADES = s.allow_real_trades

@pytest.mark.skipif(not HAS_KEYS, reason="Set Alpaca keys")
@pytest.mark.skipif(not ALLOW_TRADES, reason="Opt-in with ALLOW_REAL_TRADES=1")
def test_place_market_order():
    broker = AlpacaBroker(
        s.alpaca.key,
        s.alpaca.secret,
        s.alpaca.paper,
    )
    order = broker.place_order(OrderRequest("AAPL", 1, Side.BUY, OrderType.MARKET))
    assert order.symbol == "AAPL"
    assert order.status in {OrderStatus.NEW, OrderStatus.ACCEPTED, OrderStatus.FILLED, OrderStatus.PENDING_NEW}