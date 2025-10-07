###
# DESCR: Maps uniform/domain names and objects to BROKER specific names/requirements
# EDITS:
# 10/7/2025: added map_side, map_type, map_tif, map_tf
###

from core.domain.models import Side, OrderType, TimeInForce, Timeframe


def map_side(side: Side) -> str:
    return "buy" if side is Side.BUY else "sell"

def map_type(t: OrderType) -> str:
    return "market" if t is OrderType.MARKET else "limit"

def map_tif(t: TimeInForce) -> str:
    return {TimeInForce.DAY: "day", TimeInForce.GTC: "gtc",
            TimeInForce.IOC: "day", TimeInForce.FOK: "day"}[t]

def map_timeframe(tf: Timeframe) -> str:
    return {
        Timeframe.ONE_MIN: "1min",
        Timeframe.FIVE_MIN: "5min",
        Timeframe.FIFTEEN_MIN: "15min",
        Timeframe.ONE_HOUR: "60min",
        Timeframe.ONE_DAY: "daily",
    }[tf]