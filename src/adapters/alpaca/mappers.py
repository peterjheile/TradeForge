###
# Last edit: 10/5/25
#
# Desc: Maps broker specific values/strings to uniform values/strings
###

from core.domain.models import Timeframe as DomainTimeFrame
from core.domain.models import TimeInForce as DomainTIF
from alpaca.data.timeframe import TimeFrameUnit
from alpaca.data.timeframe import TimeFrame as AlpacaTimeFrame
from alpaca.trading.enums import TimeInForce as AlpacaTIF



def map_timeframe(tf: DomainTimeFrame) -> AlpacaTimeFrame:
    mapping = {
        DomainTimeFrame.ONE_MIN:  AlpacaTimeFrame(1,  TimeFrameUnit.Minute),
        DomainTimeFrame.FIVE_MIN: AlpacaTimeFrame(5,  TimeFrameUnit.Minute),
        DomainTimeFrame.FIFTEEN_MIN: AlpacaTimeFrame(15, TimeFrameUnit.Minute),
        DomainTimeFrame.ONE_HOUR: AlpacaTimeFrame(1,  TimeFrameUnit.Hour),
        DomainTimeFrame.ONE_DAY:  AlpacaTimeFrame(1,  TimeFrameUnit.Day),
    }
    try:
        return mapping[tf]
    except KeyError:
        raise ValueError(f"Unsupported timeframe: {tf}")


#map domain time in force to alpaca time in force34. Luckily its nearly 1 to 1
def map_time_in_force(tif: DomainTIF) -> AlpacaTIF:
    table = {
        DomainTIF.DAY: AlpacaTIF.DAY,
        DomainTIF.GTC: AlpacaTIF.GTC,
        DomainTIF.IOC: AlpacaTIF.IOC,
        DomainTIF.FOK: AlpacaTIF.FOK,
    }
    return table[tif]
