from app.providers.base import Provider, register
from adapters.alpaca.broker import AlpacaBroker
from adapters.alpaca.market_data import AlpacaMarketData



class _AlpacaProvider:
    name = "alpaca"
    def build(self, settings):
        a = settings.alpaca
        return (
            AlpacaBroker(a),
            AlpacaMarketData(a),
        )
    
register(_AlpacaProvider())