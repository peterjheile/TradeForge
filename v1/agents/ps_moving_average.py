import numpy as np
from core.signal import Signal
from core.decision import Decision

class MovingAverageAgent:

    def __init__(self, short_window=10, long_window=50):
        self.short_window = short_window
        self.long_window = long_window


    def generate_signal(self, bars):
        bars = self.api.get_bars(self.symbol, "1Min", limit=self.long_window).df
        if len(bars) < self.long_window:
            return Decision(signal=Signal.HOLD, symbol=self.symbol)

        close = bars["close"]
        short_ma = np.mean(close[-self.short_window:])
        long_ma = np.mean(close[-self.long_window:])

        if short_ma > long_ma:
            return Decision(signal=Signal.BUY, symbol=self.symbol)
        elif short_ma < long_ma:
            return Decision(signal=Signal.SELL, symbol=self.symbol)
        else:
            return Decision(signal=Signal.HOLD, symbol=self.symbol)
        






