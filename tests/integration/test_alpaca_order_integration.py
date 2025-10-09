import os
import time
import pytest

from app.settings import get_settings
from app.factory import make_adapters
from core.domain.models import (
    OrderRequest, OrderType, Side, TimeInForce, OrderStatus,
)

import time
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest



# --- Gating / environment ---
s = get_settings()
IS_ALPACA = s.provider == "alpaca" and bool(s.alpaca.key and s.alpaca.secret)
ALLOW_TRADES = s.allow_real_trades == True


pytestmark = [
    pytest.mark.skipif(not IS_ALPACA, reason="Set PROVIDER=alpaca and Alpaca keys to run"),
    pytest.mark.skipif(not ALLOW_TRADES, reason="Set ALLOW_TRADES=1 to run order placement tests"),
]

# --- Helpers / constants ---
EQUITY = "AAPL"
CRYPTO = "BTC/USD"

ACCEPTABLE_EARLY_STATUSES = {
    OrderStatus.PENDING_NEW,
    OrderStatus.NEW,
    OrderStatus.ACCEPTED,
    OrderStatus.PARTIALLY_FILLED,
    OrderStatus.FILLED,
    OrderStatus.DONE_FOR_DAY,
    OrderStatus.CALCULATED,
}





@pytest.fixture(scope="session", autouse=True)
def trading_notice(pytestconfig):
    pytestconfig.pluginmanager.get_plugin("terminalreporter").write_line(
        "\n⚠️  Please wait — live Alpaca trading tests running.\n"
        "   Orders are spaced to avoid wash-trade rejections.\n"
    )







@pytest.fixture(scope="module")
def broker():
    b, _ = make_adapters()
    return b

def _cancel_if_possible(broker, order_id: str):
    try:
        broker.cancel_order(order_id)
    except Exception:
        # It's fine if already filled/not cancelable/etc.
        pass


def _tc():
    # direct client only for cleanup/checks; uses the same settings as your broker
    s = get_settings()
    return TradingClient(s.alpaca.key, s.alpaca.secret, paper=s.alpaca.paper)




def _cancel_all_open(symbol: str):
    tc = _tc()
    # cancel all open orders for this symbol (ignore errors)
    for o in tc.get_orders(GetOrdersRequest(status=QueryOrderStatus.OPEN)):
        if o.symbol == symbol:
            try:
                tc.cancel_order_by_id(o.id)
            except Exception:
                pass



def _wait_until_filled(order_id: str, timeout=2.0, poll=0.5):
    tc = _tc()
    t0 = time.time()
    while time.time() - t0 < timeout:
        o = tc.get_order_by_id(order_id)
        if str(o.status).lower() in {"filled", "done_for_day"}:
            return True
        time.sleep(poll)
    return False



def _safe_crypto_qty():
    # choose a conservative tiny size
    return 0.0005



# -----------------------------------------------------------------------------
# MARKET orders (equity & crypto)
# -----------------------------------------------------------------------------

def test_market_equity_buy_then_sell(broker):
    _cancel_all_open(EQUITY)

    buy = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.BUY,
        type=OrderType.MARKET, time_in_force=TimeInForce.DAY
    )
    o1 = broker.place_order(buy)
    assert o1.symbol == EQUITY
    # Wait for the buy to be done so the sell won't be flagged as wash trade
    _wait_until_filled(o1.id, timeout=2)

    sell = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.SELL,
        type=OrderType.MARKET, time_in_force=TimeInForce.DAY
    )
    o2 = broker.place_order(sell)
    assert o2.symbol == EQUITY

def test_market_crypto_buy_then_sell(broker):
    _cancel_all_open(CRYPTO)
    qty = 0.0005  # smaller to avoid "insufficient balance" by a few sats

    buy = OrderRequest(
        symbol=CRYPTO, qty=qty, side=Side.BUY,
        type=OrderType.MARKET, time_in_force=TimeInForce.GTC
    )
    o1 = broker.place_order(buy)
    assert o1.symbol == CRYPTO
    _wait_until_filled(o1.id, timeout=2)

    sell = OrderRequest(
        symbol=CRYPTO, qty=qty, side=Side.SELL,
        type=OrderType.MARKET, time_in_force=TimeInForce.GTC
    )
    o2 = broker.place_order(sell)
    assert o2.symbol == CRYPTO

# -----------------------------------------------------------------------------
# LIMIT order (equity) + negative: missing limit_price
# -----------------------------------------------------------------------------

def test_limit_equity_resting_and_cancel(broker):
    # Place an ultra-low limit buy so it rests (should not fill)
    req = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.BUY,
        type=OrderType.LIMIT, time_in_force=TimeInForce.DAY,
        limit_price=1.00
    )
    o = broker.place_order(req)
    assert o.symbol == EQUITY
    assert o.status in ACCEPTABLE_EARLY_STATUSES
    # Give API a moment to register, then try to cancel
    time.sleep(0.5)
    _cancel_if_possible(broker, o.id)

def test_limit_equity_missing_price_raises(broker):
    # Your adapter should validate this and raise its own error
    with pytest.raises(Exception) as e:
        broker.place_order(OrderRequest(
            symbol=EQUITY, qty=1, side=Side.BUY,
            type=OrderType.LIMIT, time_in_force=TimeInForce.DAY
        ))
    assert "limit_price" in str(e.value).lower()

# -----------------------------------------------------------------------------
# STOP order (equity) + negative: missing stop_price
# -----------------------------------------------------------------------------

def test_stop_equity_resting_and_cancel(broker):
    _cancel_all_open(EQUITY)  # <— prevents “opposite side limit order exists”

    req = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.SELL,
        type=OrderType.STOP, time_in_force=TimeInForce.DAY,
        stop_price=1.00
    )
    o = broker.place_order(req)
    assert o.symbol == EQUITY
    time.sleep(0.5)
    _cancel_all_open(EQUITY)  # try to cancel the new stop

# -----------------------------------------------------------------------------
# STOP-LIMIT (equity) + negatives
# -----------------------------------------------------------------------------

def test_stop_limit_equity_resting_and_cancel(broker):
    # Use very low prices to avoid immediate execution
    req = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.BUY,
        type=OrderType.STOP_LIMIT, time_in_force=TimeInForce.DAY,
        stop_price=2.00, limit_price=1.50
    )
    o = broker.place_order(req)
    assert o.symbol == EQUITY
    assert o.status in ACCEPTABLE_EARLY_STATUSES
    time.sleep(0.5)
    _cancel_if_possible(broker, o.id)

def test_stop_limit_equity_missing_prices_raise(broker):
    # missing stop_price
    with pytest.raises(Exception) as e1:
        broker.place_order(OrderRequest(
            symbol=EQUITY, qty=1, side=Side.BUY,
            type=OrderType.STOP_LIMIT, time_in_force=TimeInForce.DAY,
            limit_price=10.0
        ))
    assert "stop_price" in str(e1.value).lower()

    # missing limit_price
    with pytest.raises(Exception) as e2:
        broker.place_order(OrderRequest(
            symbol=EQUITY, qty=1, side=Side.BUY,
            type=OrderType.STOP_LIMIT, time_in_force=TimeInForce.DAY,
            stop_price=10.5
        ))
    assert "limit_price" in str(e2.value).lower()

# -----------------------------------------------------------------------------
# TRAILING-STOP (equity) + negatives
# -----------------------------------------------------------------------------

def test_trailing_stop_equity_with_trail_percent(broker):
    req = OrderRequest(
        symbol=EQUITY, qty=1, side=Side.SELL,
        type=OrderType.TRAILING_STOP, time_in_force=TimeInForce.DAY,
        trail_percent=5.0
    )
    o = broker.place_order(req)
    assert o.symbol == EQUITY
    assert o.status in ACCEPTABLE_EARLY_STATUSES
    time.sleep(0.5)
    _cancel_if_possible(broker, o.id)

def test_trailing_stop_equity_param_rules(broker):
    # Neither provided
    with pytest.raises(Exception) as e0:
        broker.place_order(OrderRequest(
            symbol=EQUITY, qty=1, side=Side.SELL,
            type=OrderType.TRAILING_STOP, time_in_force=TimeInForce.DAY
        ))
    assert "trailing stop requires exactly one" in str(e0.value).lower()

    # Both provided
    with pytest.raises(Exception) as e2:
        broker.place_order(OrderRequest(
            symbol=EQUITY, qty=1, side=Side.SELL,
            type=OrderType.TRAILING_STOP, time_in_force=TimeInForce.DAY,
            trail_price=0.5, trail_percent=1.0
        ))
    assert "exactly one" in str(e2.value).lower()

# -----------------------------------------------------------------------------
# OPTIONAL: Crypto incompatibilities (documented expectations)
# -----------------------------------------------------------------------------
# If you later add pre-validation for crypto TIF and/or unsupported types, you can
# enable tests like these (expecting an exception). For now, they are commented
# to avoid flakiness while your adapter keeps basic handling.

# def test_crypto_stop_not_supported_expect_error(broker):
#     with pytest.raises(Exception):
#         broker.place_order(OrderRequest(
#             symbol=CRYPTO, qty=0.001, side=Side.SELL,
#             type=OrderType.STOP, time_in_force=TimeInForce.GTC, stop_price=1.0
#         ))