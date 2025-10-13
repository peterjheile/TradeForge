###
# EDITS:
# Desc: ENSURES EVERY FUNCTION WORKS, AND ALSO THAT ERRORS ARE RAISED ACCORDINGLY WHERE FUNCTIONS MAY BE MISUSED
# 10/7/2025: added testing for every single alpaca broker function
# 10/8/2025: more in depth tesing for each alpaca function, testing each valid alpaca api input combination (pretty much redid whole file)
###

import os
import time
import pytest

from app.settings import get_settings
from adapters.alpaca.broker import AlpacaBroker
from core.domain.models import OrderRequest, OrderStatus, TimeInForce, Side, OrderType
from utils.alpaca_constants import EQUITY_MATRIX

s = get_settings()
HAS_ALPACA_KEYS = "alpaca" in s.configured_providers()
ALLOW_TRADES = s.allow_real_trades

pytestmark = [
    pytest.mark.skipif(not HAS_ALPACA_KEYS, reason="Set APCA_API_KEY_ID / APCA_API_SECRET_KEY in .env")
]


@pytest.fixture(scope="module")
def broker():
    #build the alpaca broker directly
    return AlpacaBroker(s.alpaca)







#--------------------------------------- GET ACCOUNT ----------------------------------------#
def test_get_account(broker):
    acct=broker.get_account()
    assert isinstance(acct, dict)

    #some of the basic keys expected in the alpaca api account object
    for k in ("status", "buying_power", "portfolio_value"):
        assert k in acct
        









#--------------------------------------- GET POSITIONS ----------------------------------------#
def test_get_positions(broker):
    acct = broker.get_positions()
    assert isinstance(acct, list)
    #account may have zero positions so no reason for anon-empty assertion







#--------------------------------------- PLACE ORDER (ALL TIF, ORDER SIDES, ORDER TYPES, ASSETS) ----------------------------------------#



@pytest.mark.skipif(not ALLOW_TRADES, reason="Set ALLOW_REAL_TRADES=1 to place an orders")
def test_place_stock_order(broker):
    acct = broker
    equity_matrix = EQUITY_MATRIX

    #make every order in the equity matrtix, this tries each option for each parameter in the api broker
    for dict in equity_matrix:
        type = dict["type"]
        req = None
        match type:
            case OrderType.LIMIT.value: req = 
            case OrderType.MARKET.value:
                pass
            case OrderType.STOP.value:
                pass
            case OrderType.STOP_LIMIT.value:
                pass
            case OrderType.TRAILING_STOP.value:
                pass
            case _:
                print("Somehow an invalid case made its way in. Uh oh")

        
    



# #place an order (market)
# @pytest.mark.skipif(not ALLOW_TRADES, reason="Set ALLOW_REAL_TRADES=1 to place orders")
# def test_place_stock_order_market_buy(broker):
#     #teests every combination of 

#     req = OrderRequest(
#         symbol="AAPL",
#         qty=.1,
#         side=Side.BUY,
#         type=OrderType.MARKET,
#         time_in_force=TimeInForce.DAY,
#     )
#     order = broker.place_order(req)
#     assert order.symbol == "AAPL"
#     assert order.status in {
#         OrderStatus.PENDING_NEW,
#         OrderStatus.NEW,
#         OrderStatus.ACCEPTED,
#         OrderStatus.PARTIALLY_FILLED,
#         OrderStatus.FILLED,
#         OrderStatus.DONE_FOR_DAY,
#         OrderStatus.CALCULATED,
#     }