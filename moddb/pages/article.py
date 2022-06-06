import bs4
from .base import BaseMetaClass
from ..utils import concat_docs, LOGGER, join, get_views, get_date
from ..enums import ArticleCategory, ThumbnailType, TutorialCategory, Difficulty
from ..boxes import Profile, Thumbnail


@concat_docs
class Article(BaseMetaClass):
    """This object represents an news article, a tutorial or a feature.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    category : :class:`.ArticleCategory`
        Type of the article (news, feature)
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the article belongs to.

    Sorting
    --------
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **dateup** - order by article date, asc is most recent first, desc is oldest first
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **member** - order by member???
        * **date** - order by upload date, asc is most recent first, desc is oldest first

        Exclusive to tutorials
        * **meta** - sort by difficulty, asc is most difficult, desc is least difficult
        * **subtype** - sort by the area the tutorial covers

    Attributes
    -----------
    category : ArticleCategory
        Whether this article is a news article, a tutorial or a feature
    name : str
        The name of the article
    profile : Profile
        The profile object of the moddb model the article is for (engine, game, mod...). Can be none if it is not
        rattached to anything, such as for site news.
    tags : dict{str : str}
        A dictionary of tags with the tag names as the key and the url to the tag
        as the value.
    views : int
        Total amount of times this article was viewed
    today : int
        amount of time the article has been viewed today
    intro : int
        The intro/teaser paragraph of the article
    author : Thumbnail
        A member type thumbnail of the member who published the article
    date : datetime.datetime
        The date the article was published
    html : str
        The html of the article
    plaintext : str
        The article text without any html
    summary : str
        plaintext intro to the article
    tutorial_category : TutorialCategory
        If the article category is tutorial, this represents the area the tutorial covers, else it is None
    difficulty : Difficulty
        If the article category is tutorial, this represents how hard the tutorial is.
    """

    def __init__(self, html: bs4.BeautifulSoup):
        try:
            self.name = html.find("span", itemprop="headline").string
        except AttributeError:
            self.name = html.find("span", itemprop="heading").string

        super().__init__(html)

        raw_type = html.find("h5", string="Browse").parent.span.a.string
        self.category = ArticleCategory[raw_type.lower()]

        try:
            raw = html.find("span", string=raw_type[0:-1]).parent.parent.parent.find(
                "div", class_="table tablemenu"
            )
        except AttributeError:
            raw = html.find("span", string=raw_type).parent.parent.parent.find(
                "div", class_="table tablemenu"
            )

        try:
            self.profile = Profile(html)
        except AttributeError:
            LOGGER.info("'%s' has no profile", self.name)
            self.profile = None

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string: join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("'%s' '%s' has no tags", self.__class__.__name__, self.name)

        views_raw = raw.find("h5", string="Views").parent.span.a.string
        self.views, self.today = get_views(views_raw)

        self.intro = html.find("p", itemprop="description").string
        author = html.find("span", itemprop="author").span.a
        self.author = Thumbnail(name=author.string, url=author["href"], type=ThumbnailType.member)

        self.date = get_date(html.find("time", itemprop="datePublished")["datetime"])
        self.html = str(html.find("div", itemprop="articleBody"))
        self.plaintext = html.find("div", itemprop="articleBody").text

        self.summary = html.find("p", class_="introductiontext").string

        if self.category == ArticleCategory.tutorials:
            cat = html.find("span", itemprop="proficiencyLevel").nextSibling.strip()
            self.tutorial_category = TutorialCategory[cat.replace("/", "_").replace(" ", "_").lower()]
            self.difficulty = Difficulty[html.find("span", itemprop="proficiencyLevel").string.lower()]

    def __repr__(self):
        return f"<Article title={self.name} type={self.category.name}>"


@concat_docs
class Blog(BaseMetaClass):
    """Object used to represent a member blog.

    Filtering
    ----------
    timeframe : :class:`.TimeFrame`
        The time period this was released in (last 24hr, last week, last month)

    Sorting
    --------
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **dateup** - order by blog date, asc is most recent first, desc is oldest first
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **member** - order by member???
        * **date** - order by upload date, asc is most recent first, desc is oldest first

    Attributes
    -----------
    name_id : str
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.

    """

    def __init__(self, *, heading, text):
        author = heading.find("span", class_="subheading").a
        self.author = Thumbnail(url=author["href"], name=author.string, type=ThumbnailType.member)

        self.date = get_date(heading.find("span", class_="date").time["datetime"])

        title = heading.div.h4.a
        self.name = title.string
        self.url = join(title["href"])
        self.name_id = self.url.split("/")[0]

        self.html = str(text.content)
        self.plaintext = text.text

    def __repr__(self):
        return f"<Blog title={self.name}>"
