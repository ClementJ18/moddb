import moddb
import logging
import sys
from bs4 import BeautifulSoup

logger = logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

# o = moddb.search(moddb.SearchCategory.mods, query=" ".join(sys.argv[1:]), sort=("released", False))
# html = moddb.soup("https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods")
# poll = moddb.pages.Poll(html)

html = moddb.soup(sys.argv[2])
o = getattr(moddb.pages, sys.argv[1])(html)

# with open(f"fakes/{sys.argv[1]}.txt", "r") as f:
#     file = f
#     html = BeautifulSoup(f.read(), 'html.parser')

# o = getattr(moddb.pages, sys.argv[1].title())(html)
