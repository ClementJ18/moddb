from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import SearchCategory
from ..utils import concat_docs
from .base import PageMetaClass
from .mixins import GetAddonsMixin

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


@concat_docs
class Mod(PageMetaClass, GetAddonsMixin):
    """Basically just a subclass of Page

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    released : :class:`.Status`
        The status of the mod (released, unreleased)
    genre : :class:`.Genre`
        The genre of the mod (fps, tower defense)
    theme : :class:`.Theme`
        The theme of the mod (fantasy, action)
    players : :class:`.PlayerStyle`
        Player styles of the mod (co-op, singleplayer)
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the mod belongs to.

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **game** - order by game???
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first

    """

    def __init__(self, html: BeautifulSoup):
        super().__init__(html, SearchCategory.mods)
