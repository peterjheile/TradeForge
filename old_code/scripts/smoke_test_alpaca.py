###
# Last edit: 10/6/2025
#
# Desc: Quick smoke test for the AlpacaBroker, also uses the settings o technically tests those too
###

from app.settings import get_settings
from adapters.alpaca.broker import AlpacaBroker
from adapters.alpaca.market_data import AlpacaMarketData
from core.domain.models import OrderRequest, Side, OrderType, Timeframe


settings = get_settings()

broker = AlpacaBroker(settings.alpaca.key, settings.alpaca.secret, paper = settings.alpaca.paper)
data = AlpacaMarketData(settings.alpaca.key, settings.alpaca.secret)

print("Account:", broker.get_account())
print("Bars[0]:", (data.get_bars("AAPL", Timeframe.ONE_MIN, limit=3) or [None])[0])


print(broker.get_account())
order = broker.place_order(OrderRequest("AAPL", 1, Side.BUY, OrderType.MARKET))
print(order)