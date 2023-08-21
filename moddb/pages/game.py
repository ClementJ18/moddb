import bs4

from ..enums import SearchCategory
from ..utils import concat_docs
from .base import PageMetaClass
from .mixins import GetAddonsMixin, GetModsMixin


@concat_docs
class Game(PageMetaClass, GetModsMixin, GetAddonsMixin):
    """A subclass of Page plus a method to get all the mods.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.


    Filtering
    ----------
    released : :class:`.Status`
        The status of the game (released, unreleased)
    genre : :class:`.Genre`
        The genre of the game (fps, tower defense)
    theme : :class:`.Theme`
        The theme of the game (fantasy, action)
    indie : :class:`.Scope`
        Whether the game is triple AAA or indie
    players : :class:`.PlayerStyle`
        Player styles of the game (co-op, singleplayer)
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first
    """

    def __init__(self, html: bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.games)
