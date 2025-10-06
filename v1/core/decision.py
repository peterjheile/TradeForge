#conatins the signal class used to communicate buy/sell/hold signals and their assiciated data between the bots and the runner

from typing import Optional
from core.signal import Signal


class Decision:

    def __init__(
        self,
        symbol: str,
        signal: Signal,
        meta: Optional[dict] = None,
    ):


        self.symbol = symbol
        self.signal = signal
        self.meta = meta or {}

    def __repr__(self):
        return (
            f"Decision(symbol={self.symbol}, signal={self.signal}")
