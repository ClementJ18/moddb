from moddb.ratelimit import Ratelimit

e = Ratelimit(40, 20, 20)

import logging
logging.basicConfig(level=logging.DEBUG)

for x in range(41):
    print(x)
    e.call()