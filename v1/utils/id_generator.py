import time
from datetime import datetime, timedelta

class IDFactory:
    @staticmethod
    def generate_bot_id(agent, symbol, timestamp):
        return f"{timestamp}_{type(agent).__name__}_{symbol}"
                
    @staticmethod
    def generate_basic_id(timestamp, prefix):

        return f"{timestamp}_{prefix}"
