
from datetime import datetime, timedelta
import time
from typing import Optional

from .utils import LOGGER

class RatelimitError(Exception):
    def __init__(self, message, remaining) -> None:
        super().__init__(message)

        self.remaining = remaining


class Ratelimit:
    def __init__(self, rate: float, per: float, sleep: Optional[None] = None):
        self.rate = rate
        self.per = per
        self.sleep = sleep

        self.last_called = datetime.min
        self.initial_call = datetime.min
        self.call_count = 0

    def reset(self, now: datetime):
        self.initial_call = now
        self.call_count = 0

    def call(self):
        now = datetime.now()

        expiry = self.initial_call + timedelta(seconds=self.per)
        if now > expiry:
            self.reset(now)

        if self.call_count + 1 > self.rate:
            remaining = (expiry - now).total_seconds()
            if self.sleep is not None and remaining <= self.sleep:
                LOGGER.info("Ratelimited! Sleeping for %s", remaining)
                time.sleep(remaining)
                self.reset(now)
            else:
                raise RatelimitError(f"Ratelimited please try again in {remaining}", remaining)
            
        self.call_count += 1

        
            
