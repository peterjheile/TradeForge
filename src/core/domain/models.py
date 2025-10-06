
###
# Last edit: 10/5/2025
#
# Desc: class Models that enforce uniformity of information passed and variable definitions
###


from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional





####Enums describe fixed choices, broker-agnostic###
class Side(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class TimeInForce(str, Enum):
    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"

class OrderStatus(str, Enum):
    PENDING_NEW = "pending_new"
    NEW = "new"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    DONE_FOR_DAY = "done_for_day"
    CANCELED = "canceled"
    EXPIRED = "expired"
    REPLACED = "replaced"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"
    STOPPED = "stopped"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    CALCULATED = "calculated"

class Timeframe(str, Enum):
    ONE_MIN = "1Min"
    FIVE_MIN = "5Min"
    FIFTEEN_MIN = "15Min"
    ONE_HOUR = "1H"
    ONE_DAY = "1D"




###Requests/responses your core understands (no SDK types)
@dataclass(frozen=True)
class OrderRequest:
    symbol: str
    qty: float
    side: Side
    type: OrderType
    time_in_force: TimeInForce = TimeInForce.DAY
    limit_price: Optional[float] = None   #this is used when the type == LIMIT

@dataclass(frozen=True)
class Order:
    id: str
    symbol: str
    status: OrderStatus #defined above
    filled_qty: float
    submitted_at: Optional[str] = None
    filled_at: Optional[str] = None


@dataclass(frozen=True)
class Bar:
    t: str   #ISO timestamp
    o: float; h: float; l: float; c: float #open, high, low, close prices
    v: float  #volume