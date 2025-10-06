from app.settings import get_settings
from app.providers.base import get_provider
from core.services.account import GenericAccount


#have to make sure that provider self rgistration happens
from adapters.alpaca import provider as _

def make_adapters():
    s = get_settings()
    return get_provider(s.provider).build(s)


def make_account() -> GenericAccount:
    broker, data = make_adapters()
    return GenericAccount(broker, data)


