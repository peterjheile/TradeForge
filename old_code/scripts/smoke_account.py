from app.factory import make_account
from core.domain.models import Timeframe

acct = make_account()
print("Account:", acct.account())
print("Bars[0]:", (acct.latest_bars("AAPL", Timeframe.ONE_MIN, 3) or [None])[0])
o = acct.buy_market("AAPL", 1)
print("Order:", o)