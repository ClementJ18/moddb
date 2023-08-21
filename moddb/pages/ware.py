from ..boxes import Thumbnail
from ..enums import SearchCategory, ThumbnailType
from ..utils import LOGGER, concat_docs
from .base import HardwareSoftwareMetaClass
from .mixins import GetGamesMixin, GetWaresMixin


@concat_docs
class Hardware(HardwareSoftwareMetaClass, GetGamesMixin, GetWaresMixin):
    """Represents a moddb Hardware page

    Parameters
    -----------
    html : BeautifulSoup
        The html file to parse, allows for finer control

    Filtering
    ----------
    released : :class:`.Status`
        Release status of the hardware (released, unreleased, early access)
    category : :class:`.HardwareCategory`
        Category of the hardware
    timeframe : :class:`.TimeFrame`
        How long ago the hardware was released

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **category** - sort alphebatically by hardwarecategory
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first

    Attributes
    -----------
    hardware : List[Thumbnail]
        A list of hardware suggested on the hardware main page.
    software : List[Thumbnail]
        A list of software suggested on the hardware main page.
    games : List[Thumbnail]
        A list of games suggested on the hardware main page.
    history : List[Thumbnail]
        A list of previous iterations of the hardware
    recommended : List[Thumbnail]
        A list of recommended hardwares.
    """

    def __init__(self, html):
        super().__init__(html)
        self._type = SearchCategory.hardwares

        try:
            hardware = (
                html.find("span", string="Hardware")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)[:-1]
            )
            self.hardware = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    type=ThumbnailType.hardware,
                    image=x.a.img["src"],
                )
                for x in hardware
            ]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no hardware", self.name)
            self.hardware = []

        try:
            software = (
                html.find("span", string="Software")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)[:-1]
            )
            self.software = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    type=ThumbnailType.software,
                    image=x.a.img["src"],
                )
                for x in software
            ]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no software", self.name)
            self.software = []

        try:
            games = (
                html.find("span", string="Games")
                .parent.parent.parent.find("div", class_="table")
                .find_all("div", recursive=False)[:-1]
            )
            self.games = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    type=ThumbnailType.game,
                    image=x.a.img["src"],
                )
                for x in games
            ]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no games", self.name)
            self.games = []

        try:
            history = html.find("span", string="History").parent.parent.parent.find_all(
                "a", class_="image"
            )
            self.history = [
                Thumbnail(
                    url=x["href"],
                    name=x["title"],
                    type=ThumbnailType.hardware,
                    image=x.img["src"],
                )
                for x in history
            ]
        except AttributeError:
            LOGGER.info("Harware '%s' has no history", self.name)
            self.history = []

        try:
            recommended = html.find("span", string="Recommended").parent.parent.parent.find_all(
                "a", class_="image"
            )
            self.recommended = [
                Thumbnail(
                    url=x["href"],
                    name=x["title"],
                    type=ThumbnailType.hardware,
                    image=x.img["src"],
                )
                for x in recommended
            ]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no recommended", self.name)
            self.recommended = []


@concat_docs
class Software(HardwareSoftwareMetaClass):
    """Represents a moddb Software page

    Parameters
    -----------
    html : BeautifulSoup
        The html file to parse, allows for finer control

    Filtering
    ----------
    released : :class:`.Status`
        Release status of the software (released, unreleased, early access)
    category : :class:`.SoftwareCategory`
        Category of the software
    timeframe : :class:`.TimeFrame`
        How long ago the software was released

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **rating** - order by rating, asc is highest rating, desc is lowest rating
        * **category** - sort alphebatically by softwarecategory
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first

    """

    def __init__(self, html):
        super().__init__(html)
        self._type = SearchCategory.softwares
