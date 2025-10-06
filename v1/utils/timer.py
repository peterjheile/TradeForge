from datetime import datetime, timedelta
import time

class Timer:
    def __init__(self, interval=0, duration=None):
        self.start_time = datetime.now()   
        self.end_time = timedelta(seconds=duration) + self.start_time if duration else None
        self.interval = interval
        self.id = self.create_timestamp()

    def has_expired(self):
        return self.end_time and datetime.now() >= self.end_time
    
    def time_elapsed(self):
        return (datetime.now() - self.start_time).total_seconds()
    
    def create_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d_%H;%M;%S")
    
    def current_time(self):
        return datetime.now()
    
    def sleep_interval(self, interval=None):
        if interval: time.sleep(interval)
        else: time.sleep(self.interval)

    def set_interval(self, new_interval):
        self.interval = new_interval

    
    # def reset(self, duration=None):
    #     self.start_time = datetime.datetime.now()
    #     self.end_time = duration + self.start_time if duration else None

