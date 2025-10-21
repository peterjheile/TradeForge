from app.providers.base import Provider, register
from adapters.tradier.broker import TradierBroker
from adapters.tradier.market_data import TradierMarketData


class _TradierProvider:
    name = "tradier"
    def build(self, settings):
        t = settings.tradier
        broker = TradierBroker(t)
        data = TradierMarketData(t)
        return broker, data
    

register(_TradierProvider())