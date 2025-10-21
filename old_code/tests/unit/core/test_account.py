"""
Light unit tests for core.services.account.GenericAccount
Verifies basic orchestration and call-through behavior using mocks.
"""

###
# EDITS:
# 10/13/2025: Created file and unitest for the GenericAccount in services/account.py
###

import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from core.services.account_service import GenericAccount
from core.domain.models import (
    OrderRequest, Order, Side, OrderType, TimeInForce, Timeframe,
    Account, Position, Bar,
)


def make_mocks():
    broker = MagicMock(name="MockBroker")
    data = MagicMock(name="MockMarketData")
    return broker, data


def test_place_order_calls_broker_with_correct_request():
    broker, data = make_mocks()
    fake_order = Order(
        id="123",
        symbol="AAPL",
        status="filled",
        filled_qty=Decimal("10"),
    )
    broker.place_order.return_value = fake_order

    acct = GenericAccount(broker, data)
    result = acct.place_order(
        symbol="AAPL",
        side=Side.BUY,
        type=OrderType.MARKET,
        qty=Decimal("10"),
        tif=TimeInForce.DAY,
    )

    # Verify call
    broker.place_order.assert_called_once()
    req_arg: OrderRequest = broker.place_order.call_args[0][0]
    assert req_arg.symbol == "AAPL"
    assert req_arg.side == Side.BUY
    assert req_arg.type == OrderType.MARKET
    assert req_arg.qty == Decimal("10")
    assert result is fake_order


def test_get_bars_forwards_to_market_data():
    broker, data = make_mocks()
    fake_bars = [
        Bar(timestamp="2025-10-10T12:00:00Z", o=Decimal("1"), h=Decimal("2"), l=Decimal("1"), c=Decimal("2"), v=100)
    ]
    data.get_bars.return_value = fake_bars

    acct = GenericAccount(broker, data)
    result = acct.get_bars("AAPL", Timeframe.ONE_MIN, 1)

    data.get_bars.assert_called_once_with("AAPL", Timeframe.ONE_MIN, 1)
    assert result == fake_bars


def test_positions_and_account_are_normalized(monkeypatch):
    broker, data = make_mocks()
    fake_positions = [Position(symbol="AAPL", qty=Decimal("10"), avg_price=Decimal("150"), asset_class="equity")]
    fake_account = Account(account_id="acc-1", currency="USD", cash=Decimal("100"), equity=Decimal("200"), buying_power=Decimal("400"))

    broker.get_positions.return_value = fake_positions
    broker.get_account.return_value = fake_account

    # patch normalization to just echo back inputs
    monkeypatch.setattr("core.domain.policies.normalize_position", lambda x: x)
    monkeypatch.setattr("core.domain.policies.normalize_account", lambda x: x)

    acct = GenericAccount(broker, data)
    assert acct.positions() == fake_positions
    assert acct.account() == fake_account