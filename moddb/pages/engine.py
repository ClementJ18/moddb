import logging

import bs4

from ..enums import SearchCategory
from ..utils import LOGGER, concat_docs
from .base import PageMetaClass
from .mixins import GetGamesMixin


@concat_docs
class Engine(PageMetaClass, GetGamesMixin):
    """A subclass of Page, however, it does not have the files attribute

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    -----------
    released : :class:`.Status`
        The status of the engine (released, unreleased)
    licence : :class:`.Licence`
        The license of the engine
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

    Attributes
    -----------
    games : List[Thumbnail]
        A list of games suggested on the engine main page.
    """

    def __init__(self, html: bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.engines)
        delattr(self, "files")

        try:
            self.games = self._get_games(html)
        except AttributeError:
            LOGGER.info(
                "Engine '%s' has no games", self.name, exc_info=LOGGER.level >= logging.DEBUG
            )
            self.games = []
