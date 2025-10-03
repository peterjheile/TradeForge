from core.decision import Signal, Decision
import random


class RandomChoices:

    def __init__(self):
        pass

    def generate_Decision(self, symbol, price_data) -> Decision:


        decision = Decision(
            symbol=symbol,
            signal=random.choice([Signal.BUY, Signal.SELL, Signal.HOLD]),
        )

        return decision
        



