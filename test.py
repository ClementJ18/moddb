from pyrate_limiter import Duration, Limiter, Rate

GLOBAL_THROTTLE = Duration.MINUTE * 5
GLOBAL_LIMITER = Limiter(
    [
        # request stuff slowly, like a human
        Rate(1, Duration.SECOND * 1),
        # take breaks when requesting stuff, like a human
        Rate(40, GLOBAL_THROTTLE),
    ],
    max_delay=GLOBAL_THROTTLE + 500,
)

global_limiter_decorator = GLOBAL_LIMITER.as_decorator()


def mapping(*args, **kwargs):
    return ("moddb", 1)


def ratelimit(func):
    return global_limiter_decorator(mapping)(func)

@ratelimit
def ratelimited_function(x):
    print(x)

def test_ratelimit():
    for x in range(41):
        ratelimited_function(x)

if __name__ == "__main__":
    test_ratelimit()