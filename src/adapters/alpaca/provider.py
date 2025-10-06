from app.providers.base import Provider, register
from adapters.alpaca.broker import AlpacaBroker
from adapters.alpaca.market_data import AlpacaMarketData



class _AlpacaProvider:
    name = "alpaca"
    def build(self, settings):
        a = settings.alpaca
        return (
            AlpacaBroker(a.key, a.secret, paper=a.paper),
            AlpacaMarketData(a.key, a.secret),
        )
    
register(_AlpacaProvider())