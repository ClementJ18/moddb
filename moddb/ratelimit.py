from datetime import datetime, timedelta
import functools
import time
from typing import Optional

from .utils import LOGGER
from .errors import Ratelimited


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
            LOGGER.info("Reseting ratelimit")
            self.reset(now)

        if self.call_count + 1 > self.rate:
            remaining = (expiry - now).total_seconds()
            if self.sleep is not None and remaining <= self.sleep:
                LOGGER.info("Ratelimited! Sleeping for %s", remaining)
                time.sleep(remaining)
                self.reset(now)
            else:
                raise Ratelimited(f"Ratelimited please try again in {remaining}", remaining)

        self.call_count += 1


def ratelimit(*limiters: Ratelimit):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for limiter in limiters:
                limiter.call()

            func(*args, **kwargs)

        return wrapper

    return decorator


GLOBAL_LIMITER = Ratelimit(40, 300, sleep=300)
GLOBAL_THROTLE = Ratelimit(5, 1, sleep=1)
COMMENT_LIMITER = Ratelimit(1, 60)
LOGIN_LIMITER = Ratelimit(1, 5)
