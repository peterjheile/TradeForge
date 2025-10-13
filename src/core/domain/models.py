
###
# EDITS:
# 10/xx/2025: A lot of edits and editions I did not document
# 10/13/2025: changes price values to decimal instead of float, datatime object for filled dates
# 10/13/2025: added docstring, added universal data validation
# 10/13/2025: added a generic position and account to the domain
###


"""
core.domain.models
------------------
Defines the core domain models used throughout the trading system.

These dataclasses and enumerations describe broker-agnostic trading concepts
such as order types, time-in-force policies, asset classes, and canonical
order statuses. They form the foundation of the domain layer and ensure that
data passed between adapters, policies, and use cases remains consistent,
validated, and independent of any specific broker SDK.
"""



from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from decimal import Decimal
from datetime import datetime





# ---------------------------------------------------------------------------
# ENUMERATIONS
# ---------------------------------------------------------------------------
class Side(str, Enum):
    """Represents the trade direction."""

    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    """Enumerates supported order execution types."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"

class TimeInForce(str, Enum):
    """Defines the order duration policy across brokers."""

    DAY = "day"
    GTC = "gtc"
    IOC = "ioc"
    FOK = "fok"
    OPG = "opg"
    CLS = "cls"



class OrderStatus(str, Enum):
    """Canonical set of lifecycle statuses recognized by the system.

    Broker-specific statuses are normalized to these common values
    to simplify downstream processing, logging, and analytics.
    """
        
    PENDING = "pending"
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELED = "canceled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REPLACED = "replaced"



class AssetClass(str, Enum):
    """Enumerates tradable asset classes supported by the domain."""

    EQUITY = "equity"
    CRYPTO = "crypto"
    OPTION = "option"



class Timeframe(str, Enum):
    """Defines canonical time intervals for market data aggregation."""

    ONE_MIN = "1Min"
    FIVE_MIN = "5Min"
    FIFTEEN_MIN = "15Min"
    ONE_HOUR = "1H"
    ONE_DAY = "1D"




# ---------------------------------------------------------------------------
# DATA MODELS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class OrderRequest:
    """A broker-agnostic request to submit an order.

    This dataclass represents the minimal information required to
    construct a valid trading order, independent of any broker SDK.
    It enforces logical consistency between order fields—such as
    quantity versus notional and valid price fields per order type—
    before the request is passed to a broker policy or adapter layer.

    Attributes:
        symbol: The trading symbol (e.g., 'AAPL').
        qty: The quantity of shares, units, or contracts to trade.
        notional: Dollar-based order value (exclusive with qty).
        side: Buy or sell side of the trade.
        type: The order execution type (market, limit, stop, etc.).
        time_in_force: How long the order remains active.
        limit_price: Required for limit and stop-limit orders.
        stop_price: Required for stop and stop-limit orders.
        trail_price: Fixed-dollar trailing distance for trailing stops.
        trail_percent: Percentage-based trailing distance.
        client_order_id: Optional client-supplied identifier.
        asset_class: The asset class of the instrument.
    """



    symbol: str
    side: Side
    type: OrderType
    time_in_force: TimeInForce = TimeInForce.DAY
    qty: Optional[Decimal] = None
    notional: Optional[Decimal] = None  #support dollar based orders
    limit_price: Optional[Decimal] = None   #this is used when the type == LIMIT STOP_LIMIT
    stop_price: Optional[Decimal] = None #this is used when the type == STOP or STOP_LIMIT
    trail_price: Optional[Decimal] = None #used when type == TRAILING_STOP
    trail_percent: Optional[Decimal] = None #used when type == TRAILING_STOP
    client_order_id: Optional[str] = None
    asset_class: AssetClass = AssetClass.EQUITY

    def __post_init__(self):
        """Perform core validation to ensure internal consistency."""
        if (self.qty is None and self.notional is None) or (
            self.qty is not None and self.notional is not None
        ):
            raise ValueError("Exactly one of qty or notional must be provided")

        if self.qty is not None and self.qty <= 0:
            raise ValueError("qty must be > 0")
        if self.notional is not None and self.notional <= 0:
            raise ValueError("notional must be > 0")

        match self.type:
            case OrderType.MARKET:
                if any((self.limit_price, self.stop_price, self.trail_price, self.trail_percent)):
                    raise ValueError("MARKET orders cannot include limit, stop, or trailing fields")

            case OrderType.LIMIT:
                if self.limit_price is None:
                    raise ValueError("LIMIT orders require limit_price")
                if any((self.stop_price, self.trail_price, self.trail_percent)):
                    raise ValueError("LIMIT orders may not include stop or trailing fields")

            case OrderType.STOP:
                if self.stop_price is None:
                    raise ValueError("STOP orders require stop_price")
                if any((self.limit_price, self.trail_price, self.trail_percent)):
                    raise ValueError("STOP orders may not include limit or trailing fields")

            case OrderType.STOP_LIMIT:
                if self.limit_price is None or self.stop_price is None:
                    raise ValueError("STOP_LIMIT orders require both stop_price and limit_price")
                if any((self.trail_price, self.trail_percent)):
                    raise ValueError("STOP_LIMIT orders may not include trailing fields")

            case OrderType.TRAILING_STOP:
                if (self.trail_price is None) == (self.trail_percent is None):
                    raise ValueError("TRAILING_STOP requires exactly one of trail_price or trail_percent")
                if any((self.limit_price, self.stop_price)):
                    raise ValueError("TRAILING_STOP may not include limit or stop fields")

        # Shared numeric validations
        for p in (self.limit_price, self.stop_price, self.trail_price):
            if p is not None and p <= 0:
                raise ValueError("price fields must be > 0")

        if self.trail_percent is not None and self.trail_percent <= 0:
            raise ValueError("trail_percent must be > 0")


@dataclass(frozen=True)
class Order:
    """Represents an order returned by a broker or internal tracking.

    Contains canonical order information used across the system along
    with optional broker-specific fields for reconciliation, logging,
    and audit purposes.

    Attributes:
        id: Broker-assigned or internally generated order ID.
        symbol: The trading symbol associated with the order.
        status: Canonical normalized order status.
        filled_qty: Total filled quantity.
        submitted_at: UTC datetime when the order was submitted.
        filled_at: UTC datetime when the order was completely filled.
        client_order_id: Optional client-supplied ID for matching requests.
        raw_status: The original status string from the broker API.
        raw_payload: The full broker API response for debugging/auditing.
    """


    id: str
    symbol: str
    status: OrderStatus
    filled_qty: Decimal
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    client_order_id: Optional[str] = None
    raw_status: Optional[str] = None  # broker-specific
    raw_payload: Optional[dict] = None  # debug/audit


@dataclass(frozen=True)
class Bar:
    """Represents a single OHLCV (Open, High, Low, Close, Volume) data bar.

    Used to encapsulate normalized market data retrieved from brokers
    or historical data sources. Provides consistent access to price and
    volume data regardless of broker-specific field names.

    Attributes:
        timestamp: UTC timestamp of the bar's open time.
        o: Opening price for the bar.
        h: Highest price reached during the interval.
        l: Lowest price reached during the interval.
        c: Closing price for the bar.
        v: Total traded volume during the interval.
    """

    timestamp: datetime
    o: Decimal #open
    h: Decimal #high
    l: Decimal #low
    c: Decimal #close
    v: int  #volume







# ---------------------------------------------------------------------------
# ACCOUNT AND POSITION MODELS
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Position:
    """Represents a normalized open position held in a trading account.

    All brokers map their raw position payloads to this shape to ensure
    consistency across adapters. Decimal fields maintain precision for
    financial calculations.

    Attributes:
        symbol: The trading symbol (e.g., 'AAPL', 'BTC/USD').
        asset_class: Asset class ('equity', 'crypto', 'option', etc.).
        qty: Net position size (positive = long, negative = short).
        avg_price: Average fill price of the current position.
        market_value: Current market value of the position.
        unrealized_pl: Unrealized profit or loss (positive or negative).
        updated_at: UTC timestamp of the last known update.
    """
    symbol: str
    asset_class: AssetClass
    qty: Decimal
    avg_price: Decimal
    market_value: Optional[Decimal] = None
    unrealized_pl: Optional[Decimal] = None
    updated_at: Optional[datetime] = None



@dataclass(frozen=True)
class Account:
    """Represents a normalized brokerage account snapshot.

    Provides minimal but essential financial metrics common across
    brokers. Concrete adapters populate additional fields as needed.

    Attributes:
        account_id: Unique broker-assigned account identifier.
        currency: Base currency of the account (e.g., 'USD').
        cash: Current available cash balance.
        equity: Total account equity (cash + positions).
        buying_power: Usable buying power for new trades.
        pattern_day_trader: Flag indicating PDT status (equities only).
        updated_at: UTC timestamp of the last known update.
    """
    account_id: str
    currency: str
    cash: Decimal
    equity: Decimal
    buying_power: Decimal
    pattern_day_trader: bool = False
    updated_at: Optional[datetime] = None