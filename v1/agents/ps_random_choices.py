from core.decision import Signal, Decision
import random


class RandomChoicesAgent:

    def __init__(self):
        pass

    def generate_decision(self, symbol, price_data) -> Decision:


        decision = Decision(
            symbol=symbol,
            signal=random.choice([Signal.BUY, Signal.SELL, Signal.HOLD]),
        )

        return decision
        



