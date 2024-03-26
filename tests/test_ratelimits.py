import time
import pytest

from moddb.errors import Ratelimited
from moddb.utils import Ratelimit, ratelimit


@pytest.mark.parametrize(["rate", "per"], ((1, 5), (40, 300)))
def test_ratelimit_get_limited(rate: float, per: float):
    limiter = Ratelimit(rate, per)
    for _ in range(rate):
        limiter.call()

    with pytest.raises(Ratelimited):
        limiter.call()


@pytest.mark.parametrize(["rate", "per"], ((1, 5),))
def test_ratelimit_stay_under(rate: float, per: float):
    limiter = Ratelimit(rate, per)
    for _ in range(limiter.rate * 5):
        limiter.call()
        time.sleep((limiter.per / limiter.rate) + 0.001)


def test_early_initial():
    limiter = Ratelimit(10, 2)
    limiter.call()

    time.sleep(4)

    limiter.call()

    time.sleep(1)

    limiter.call()


def test_late_burst(freezer):
    limiter = Ratelimit(10, 4)
    limiter.call()

    freezer.tick(3)
    limiter.call()

    freezer.tick(2)

    with pytest.raises(Ratelimited):
        for _ in range(11):
            limiter.call()


def test_decorator():
    limiter = Ratelimit(5, 1, sleep=1)

    @ratelimit(limiter)
    def ratelimited_function():
        return "test"

    assert ratelimited_function() == "test"

    for _ in range(6):
        ratelimited_function()
