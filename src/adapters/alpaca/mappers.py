###
# EDITS
# Desc: Maps uniform/domain names and objects to BROKER specific names/requirements
# 10/6/2025: Added mappings for each Domain Enum to Alpaca Enum/expected strings
# 10/8/2025: Added Error Handling for invalid/unexpected inputs
###

#domain
from core.domain.models import Timeframe as DomainTF
from core.domain.models import TimeInForce as DomainTIF
from core.domain.models import OrderType as DomainOT
from core.domain.models import Side as DomainSide

#alpaca
from alpaca.data.timeframe import TimeFrameUnit
from alpaca.data.timeframe import TimeFrame as AlpacaTimeFrame
from alpaca.trading.enums import TimeInForce as AlpacaTIF
from alpaca.trading.enums import OrderSide as AlpacaSide
from alpaca.trading.enums import OrderType as AlpacaOT



#NOTE: I will likely need to change these function names if I want each adapter's mappers to be able to be imported by tyhe user
__all__ = ["map_timeframe", "map_time_in_force", "map_side", "map_order_type"]



#list off the allowed choices from a given enumeration
def _choices(enum_cls) -> str:
    try:
        return ", ".join(e.value for e in enum_cls)
    except Exception:
        #fallback to names
        return ", ".join(e.name for e in enum_cls)



def map_timeframe(tf: DomainTF) -> AlpacaTimeFrame:
    mapping = {
        DomainTF.ONE_MIN: AlpacaTimeFrame(1,  TimeFrameUnit.Minute),
        DomainTF.FIVE_MIN: AlpacaTimeFrame(5,  TimeFrameUnit.Minute),
        DomainTF.FIFTEEN_MIN: AlpacaTimeFrame(15, TimeFrameUnit.Minute),
        DomainTF.ONE_HOUR: AlpacaTimeFrame(1,  TimeFrameUnit.Hour),
        DomainTF.ONE_DAY: AlpacaTimeFrame(1,  TimeFrameUnit.Day),
    }
    out = mapping.get(tf)
    if out is None:
        raise ValueError(f"Unsupported Timeframe: {tf!r}. Allowed: {_choices(DomainTF)}")
    return out


#map domain time in force to alpaca time in force34. Luckily its nearly 1 to 1
def map_time_in_force(tif: DomainTIF) -> AlpacaTIF:
    mapping = {
        DomainTIF.DAY: AlpacaTIF.DAY,
        DomainTIF.GTC: AlpacaTIF.GTC,
        DomainTIF.IOC: AlpacaTIF.IOC,
        DomainTIF.FOK: AlpacaTIF.FOK,
        DomainTIF.OPG: AlpacaTIF.OPG,
        DomainTIF.CLS: AlpacaTIF.CLS,
    }
    out = mapping.get(tif)
    if out is None:
        raise ValueError(f"Unsupported TimeInForce: {tif!r}. Allowed: {_choices(DomainTIF)}")
    return out

def map_side(side: DomainSide) -> AlpacaSide:
    mapping = {
        DomainSide.BUY:  AlpacaSide.BUY,
        DomainSide.SELL: AlpacaSide.SELL,
    }
    out = mapping.get(side)
    if out is None:
        raise ValueError(f"Unsupported Side: {side!r}. Allowed: {_choices(DomainSide)}")
    return out


def map_order_type(ot: DomainOT) -> AlpacaOT:
    mapping = {
        DomainOT.MARKET: AlpacaOT.MARKET,
        DomainOT.LIMIT: AlpacaOT.LIMIT,
        DomainOT.STOP: AlpacaOT.STOP,
        DomainOT.STOP_LIMIT: AlpacaOT.STOP_LIMIT,
        DomainOT.TRAILING_STOP: AlpacaOT.TRAILING_STOP,
    }
    out = mapping.get(ot)
    if out is None:
        raise ValueError(f"Unsupported OrderType: {ot!r}. Allowed: {_choices(DomainOT)}")
    return out

