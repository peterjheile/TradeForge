from core.domain.models import TimeInForce as TIF
from core.domain.models import Side as SIDE
from core.domain.models import OrderType as OT



#Creates a list of VALID orders that uses every VALID parameter combination once.
#Each order should represent a valid case under Alpaca rules.
#note that flags are infered and not neccessarily a focus of this test (such as limit price or day extended hours)
EQUITY_MATRIX = [
    # market
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.MARKET.value, "tif": TIF.DAY.value},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.MARKET.value, "tif": TIF.IOC.value},

    # limit
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.LIMIT.value, "tif": TIF.GTC.value, "limit_price": "1"},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.LIMIT.value, "tif": TIF.OPG.value,"limit_price": "1"},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.LIMIT.value, "tif": TIF.CLS.value, "limit_price": "1"},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.LIMIT.value, "tif": TIF.FOK.value, "limit_price": "1"},

    # stop / stop_limit
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.STOP.value, "tif": TIF.DAY.value, "stop_price": "9999"},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.STOP_LIMIT.value, "tif": TIF.GTC.value,
     "stop_price": "9999", "limit_price": "9999"},

    # trailing_stop (both TIFs)
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.TRAILING_STOP.value, "tif": TIF.DAY.value,
     "trail_percent": "1"},
    {"symbol": "AAPL", "side": SIDE.BUY.value, "type": OT.TRAILING_STOP.value, "tif": TIF.GTC.value,
     "trail_percent": "1"},

    # SELL sanity check
    {"symbol": "SPY", "side": SIDE.SELL.value, "type": OT.LIMIT.value, "tif": TIF.GTC.value,
     "limit_price": "1"},
]






#BUY adn # SELL have same exact parameters for alpaca so what will work for buy will also work for sell
#stock -> Market, Limit, Stop Limit, Stop, Trailing Stop
#Market -> day, gtc, opg, cls, ioc, fok
#Limit -> day, day extended hours (set as a flag, may ignore for now), gtc, opg, cls, ioc, fok
#Stop -> day, gtc, opg, cls, ioc, fok
#stop limit -> day, gtc, opg, cls, ioc, fok
#trailing stop -> day, gtc


#BUY
#crypto -> Market, Limit, Stop Limit
#market -> gtc, ioc
#Limit -> gtc, ioc
#stop limit -> gtc, ioc

#SELL
#same params as buy for crypto AND equities
#alpaca treats equites and ETFS the same for trading







#equity: cant test equities except on live account
