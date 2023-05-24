import enum


class SearchCategory(enum.Enum):
    """The list of things you can search for"""

    games = 0
    mods = 1
    addons = 2
    downloads = 3
    videos = 4
    articles = 5
    engines = 6
    developers = 7
    groups = 8
    forum = 9
    jobs = 10
    images = 11
    audio = 12
    reviews = 13
    headlines = 14
    blogs = 15
    hardwares = 16
    softwares = 17
    members = 18
    news = articles
    tutorials = articles
    companys = developers
    features = articles


class Category(enum.Enum):
    """Enum for the different areas of the site which things can be attached to"""

    mods = "mods"
    games = "games"
    engines = "engines"
    downloads = "downloads"


class RSSType(enum.Enum):
    """Enum to define the type of RSS you want to get from this page"""

    articles = 0
    downloads = 1
    images = 2
    videos = 3
    tutorials = 4
    reviews = 5
    addons = 6
    blogs = 7
    headlines = 8
    news = 9
    audio = 10
    jobs = 11
    poll = 12


class MediaCategory(enum.Enum):
    """What category a media object is, use for read purposes."""

    video = 0
    image = 1
    audio = 2


class ArticleCategory(enum.Enum):
    """Category of the article"""

    news = 1
    features = 2
    tutorials = 4


class Membership(enum.Enum):
    """Member ship settings of Groups and Teams"""

    invitation = 1
    application = 2
    open_to_all = 3


class TeamCategory(enum.IntFlag):
    """Category of companies, either publisher, developer or both"""

    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return self._name_
        members, uncovered = enum._decompose(cls, self._value_)
        return "|".join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    developer = 3
    publisher = 4


class ThumbnailType(enum.Enum):
    """The various types of thunbails that can be created"""

    mod = 0
    game = 1
    engine = 2
    member = 3
    group = 4
    article = 5
    review = 6
    team = 7
    blog = 8
    addon = 9
    file = 10
    job = 11
    platform = 12
    media = 13
    software = 14
    hardware = 15
    company = team


class PlayerStyle(enum.IntFlag):
    """The player style of the game"""

    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return self._name_
        members, uncovered = enum._decompose(cls, self._value_)
        return "|".join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    singleplayer = 1
    multiplayer = 2
    coop = 4
    mmo = 8


class TimeFrame(enum.Enum):
    """How recently the page was updated/uploaded, 24 hours, last week, last month, ect..."""

    day = 1
    week = 2
    month = 3
    year = 4
    more = 5


class WatchType(enum.Enum):
    mod = 0
    game = 1
    engine = 2
    group = 3
    member = 4


class Month(enum.Enum):
    january = "01"
    february = "02"
    march = "03"
    april = "04"
    may = "05"
    june = "06"
    july = "07"
    august = "08"
    september = "09"
    october = "10"
    november = "11"
    december = "12"


# BELOW THIS LINE ENUMS ARE GENERATED AUTOMATICALLY
# PR changes to scripts/generate_enums.py if you want to
# change something

