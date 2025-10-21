from typing import Protocol, Tuple, Dict
from core.ports.broker import Broker
from core.ports.market_data import MarketData

class Provider(Protocol):
    name: str
    def build(self, settings) -> Tuple[Broker, MarketData]: ...

_REGISTRY: Dict[str, Provider] = {}

def register(provider: Provider) -> None:
    if provider.name in _REGISTRY:
        raise ValueError(f"Provider '{provider.name}' already registered")
    _REGISTRY[provider.name] = provider

def get_provider(name: str) -> Provider:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown provider '{name}'. Registered: {list(_REGISTRY)}")