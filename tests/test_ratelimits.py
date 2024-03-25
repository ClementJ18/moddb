import time
import pytest

from moddb.errors import Ratelimited
from moddb.ratelimit import Ratelimit


@pytest.mark.parametrize(["rate", "per"], ((1, 5), (40, 300)))
def test_ratelimit_get_limited(rate: float, per: float):
    ratelimit = Ratelimit(rate, per)
    for _ in range(rate):
        ratelimit.call()

    with pytest.raises(Ratelimited):
        ratelimit.call()


@pytest.mark.parametrize(["rate", "per"], ((1, 5),))
def test_ratelimit_stay_under(rate: float, per: float):
    ratelimit = Ratelimit(rate, per)
    for _ in range(ratelimit.rate * 5):
        ratelimit.call()
        time.sleep((ratelimit.per / ratelimit.rate) + 0.001)


def test_early_initial():
    ratelimit = Ratelimit(10, 2)
    ratelimit.call()

    time.sleep(4)

    ratelimit.call()

    time.sleep(1)

    ratelimit.call()


def test_late_burst(freezer):
    ratelimit = Ratelimit(10, 4)
    ratelimit.call()

    freezer.tick(3)
    ratelimit.call()

    freezer.tick(2)
    for _ in range(11):
        ratelimit.call()
