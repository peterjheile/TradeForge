from core.services.account import GenericAccount
from core.domain.models import Order, Bar, Side, OrderType, Timeframe



class FakeBroker:
    last_req = None
    def place_order(self, req):
        self.last_req = req
        return Order(id="1", symbol=req.symbol, status="accepted", filled_qty=0.0)
    def cancel_order(self, order_id): pass
    def get_positions(self): return [{"symbol":"AAPL","qty":"1"}]
    def get_account(self): return {"cash":"10000"}

class FakeData:
    def get_bars(self, symbol, timeframe, limit=100):
        return [Bar("1970-01-01T00:00:00Z", 1, 2, 0.5, 1.5, 123)]
    def stream_trades(self, symbol, on_trade): pass



def test_buy_market_and_bars():
    acct = GenericAccount(FakeBroker(), FakeData())

    # buy
    order = acct.buy_market("AAPL", 1)
    assert order.symbol == "AAPL"
    # verify the façade sent the right request shape
    br = acct._broker  # test-only peek
    assert br.last_req.symbol == "AAPL"
    assert br.last_req.side is Side.BUY
    assert br.last_req.type is OrderType.MARKET

    # bars
    bars = acct.latest_bars("AAPL", Timeframe.ONE_MIN, 1)
    assert len(bars) == 1
    assert bars[0].c == 1.5

def test_account_and_positions():
    acct = GenericAccount(FakeBroker(), FakeData())
    assert acct.account()["cash"] == "10000"
    assert acct.positions()[0]["symbol"] == "AAPL"