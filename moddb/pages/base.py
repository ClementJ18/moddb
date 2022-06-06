import re
import bs4
from typing import List

from ..utils import (
    join,
    LOGGER,
    get_page,
    get_date,
    get_media_type,
    get_page_type,
)
from ..boxes import (
    CommentList,
    Thumbnail,
    ResultList,
    Profile,
    Statistics,
    PartialArticle,
    Style,
    _parse_comments,
    _parse_results,
)
from ..enums import ThumbnailType, SearchCategory
from .mixins import SharedMethodsMixin, RSSFeedMixin, GetWatchersMixin


class BaseMetaClass:
    """An abstract class that implements the attributes present on nearly every page. In addition, it implements
    some shared hidden methods and the top level get_comments method.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html containing the comments

    Attributes
    -----------
    id : int
        The id of the page
    name_id : str
        The name_id of the entity, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.
    url : str
        The url of the page
    comments : CommentList[Comment]
        The comments scrapped on this list in order.
    report : str
        URL to report the page
    """

    def __init__(self, html):
        if not getattr(self, "name", None):
            try:
                self.name = html.find("a", itemprop="mainEntityOfPage").string
            except AttributeError:
                self.name = html.find("meta", property="og:title")["content"]

        try:
            self.id = int(
                re.search(
                    r"siteareaid=(\d*)", html.find("a", class_=["reporticon"])["href"]
                )[1]
            )
        except TypeError:
            try:
                self.id = int(html.find("input", attrs={"name": "siteareaid"})["value"])
            except (AttributeError, TypeError):
                # really scratching the bottom here but a lot of "official" groups don't have the regular ID
                self.id = int(
                    html.find("meta", property="og:image")["content"].split("/")[-2]
                )

        try:
            self.url = html.find("meta", property="og:url")["content"]
        except TypeError:
            self.url = join(html.find("a", string=self.name)["href"])

        self.name_id = self.url.split("/")[-1]

        try:
            self.report = join(html.find("a", string="Report")["href"])
        except TypeError:
            self.report = None
            LOGGER.info(
                "'%s' '%s' cannot be reported", self.__class__.__name__, self.name
            )

        self.comments = self._get_comments(html)

        self._html = html

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

    def _get_comments(self, html: bs4.BeautifulSoup) -> CommentList:
        """Extracts the comments from an html page and adds them to a CommentList.

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The html containing the comments

        Returns
        --------
        CommentList
            The list of parsed comments
        """
        results, current_page, total_pages, total_results = _parse_comments(html)

        return CommentList(
            results=results,
            current_page=current_page,
            total_pages=total_pages,
            url=self.url,
            total_results=total_results,
        )

    def _get(self, url: str, *, params: dict = {}) -> ResultList:
        """This function takes a list of thumbnails of `object_type` in html and returns
        a list of Thumbnail of that object type.

        Parameters
        -----------
        url : str
            The url with the list
        object_type : ThumbnailType
            The type of objects to be expected. Easier to pass and hardcode then to guess
        params : dict
            A dictionnary of filters to pass on to the soup function used to filter the results.

        Returns
        -------
        ResultList[Thumbnail]
            The list of objects present on the page as a list of thumbnails.
        """
        html = get_page(url, params=params)
        results, current_page, total_pages, total_results = _parse_results(html)

        return ResultList(
            results=results,
            params=params,
            url=url,
            current_page=current_page,
            total_pages=total_pages,
            total_results=total_results,
        )

    def _get_media(self, index: int, *, html) -> List[Thumbnail]:
        """Hidden method used to parse media content from the page. Since the only difference is that pages
        with videos have one extra script that tells the window not do any sort of video playing assistance.
        Also used to cached all media on a page.

        Parameters
        ----------
        index : int
            The index of the script containing the cached objects. 1 if it's only images, 2 if videos are
            also included

        Returns
        --------
        List[Thumbnail]
            List of media like thumbnails that can be parsed individually. Can be a very long list.
        """
        script = html.find_all("script", text=True)[index]
        regex = r'new Array\(0, "(\S*)", "(\S*)"'
        matches = re.findall(regex, script.text)

        name_finder = r"\/([a-z0-9-]*)#imagebox"
        return [
            Thumbnail(
                name=re.search(name_finder, match[0])[1],
                url=match[0],
                type=ThumbnailType.media,
                image=match[1],
            )
            for match in matches
        ]

    def get_comments(self, index: int = 1, *, show_deleted=False) -> CommentList:
        """Used to get comments on the model regardless of what page they may be present in. The function
        itself simply relies on two other to make the request and parse the table.

        Parameters
        ----------
        index : int
            The page of the model to get the comments for.
        show_deleted : Optional[bool]
            Pass true to show deleted user comments. Only works if it is a page
            you have permissions on.

        Returns
        --------
        CommentList[Comment]
            A list-like object containing the comments and additional methods
        """
        params = {"deleted": "t" if show_deleted else None}
        return self._get_comments(get_page(f"{self.url}/page/{index}", params=params))


class PageMetaClass(BaseMetaClass, SharedMethodsMixin, RSSFeedMixin, GetWatchersMixin):
    """The common class representing the page for either a Mod, Game, Engine or a Member. Mostly used to be inherited by
    those classes.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The page to be parsed.

    page_type : ThumbnailType
        The type of pages, this is passed down be the base class to help with the parsing of

    Attributes
    -----------
    name : str
        The name of the page
    profile : Profile
        The object with the content of the page's profile box.
    stats : Statistics
        The object containg stat data on the page such as views, followers, ect...
    style : Style
        The object containing data relevant to the type of the page, not valid for Engines. Multiplayer, singleplayer,
        ect...
    suggestions : List[Thumbnail]
        A list of thumbnail object representing moddb's suggestion of similar pages for the visiting member.
    files : List[Thumbnail]
        A list of thumbnails representing a possible partial list of all the files. To get a guaranteed full
        list either compare with statistics.files to see if the length of the list matches the number of files in the
        stats or use get_files, although that will still not return the whole list if there are multiple pages of
        files.
    articles : List[Thumbnail]
        A list of thumbnail objects representing articles present on the page. Usually 3 or 4 articles long.
    article :  PartialArticle
        A partial representation of the frong page article. This does not include things like comments or any
        of the sideba elements found in a full article. Can be parsed to return the complete Article object.
    tags : dict{str : str}
        A dict of key-values pair where the key is the name of the tag and the value is the url.
    imagebox : List[Thumbnail]
        A list of Thumbnail objects representing the image, videos and audio clips that are presented in the
        image box on the front page.
    embed : str
        The html necessary to embed the a widget of the page.
    rating : float
        A float out of ten representing the average rating for the page
    medias : List[Thumbnail]
        list of thumbnails representing all the combined media objects of a page (videos and images)
    summary : str
        Short description of the page, in plaintext.
    description : str
        The full description of the page, contains html
    plaintext : str
        Plaintext version of the full description
    """

    def __init__(self, html: bs4.BeautifulSoup, page_type: SearchCategory):
        super().__init__(html)
        self._type = page_type

        # boxes
        if page_type != SearchCategory.members:
            self.profile = Profile(html)

            try:
                self.stats = Statistics(html)
            except AttributeError:
                LOGGER.info("Entity '%s' has no stats (idk why, ask moddb)", self.name)
                self.stats = None

            if page_type != SearchCategory.engines:
                self.style = Style(html)

            # thumbnails
            self.suggestions = self._get_suggestions(html)

            # misc
            try:
                self.embed = html.find("input", type="text", class_="text textembed")[
                    "value"
                ]
            except TypeError:
                self.embed = str(html.find_all("textarea")[1].a)

        try:
            self.files = self._get_files(html)
        except AttributeError:
            LOGGER.info("'%s' '%s' has no files", self.__class__.__name__, self.name)
            self.files = []

        articles_raw = None
        try:
            raw = html.find("span", string="Articles") or html.find(
                "span", string="Related Articles"
            )
            articles_raw = raw.parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    image=x.a.img["src"] if x.a.img else None,
                    summary=x.find("p").string,
                    date=x.find("time")["datetime"],
                    type=ThumbnailType.article,
                )
                for x in thumbnails
            ]
        except AttributeError:
            LOGGER.info(
                "'%s' '%s' has no article suggestions",
                self.__class__.__name__,
                self.name,
            )
            self.articles = []

        # main page article
        if articles_raw:
            self.article = PartialArticle(articles_raw)
        else:
            self.article = None
            LOGGER.info(
                "'%s' '%s' has no front page article",
                self.__class__.__name__,
                self.name,
            )

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {
                x.string: join(x["href"]) for x in raw_tags if x.string is not None
            }
        except AttributeError:
            self.tags = {}
            LOGGER.info("'%s' '%s' has no tags", self.__class__.__name__, self.name)

        # imagebox
        try:
            imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
            self.imagebox = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    image=x.a.img["src"],
                    type=ThumbnailType(get_media_type(x.a.img)),
                )
                for x in imagebox
                if x.a
            ]
        except (AttributeError, TypeError):
            LOGGER.info("'%s' '%s' has no images", self.__class__.__name__, self.name)
            self.imagebox = []

        try:
            self.rating = float(
                html.find("div", class_="score").find("meta", itemprop="ratingValue")[
                    "content"
                ]
            )
        except AttributeError:
            self.rating = 0.0
            LOGGER.info("'%s' '%s' is not rated", self.__class__.__name__, self.name)

        try:
            self._review_hash = html.find("form", class_="ratingform").find(
                "input", {"name": "hash"}
            )["value"]
        except AttributeError:
            self._review_hash = None

        self.medias = self._get_media(2, html=html)

        try:
            self.summary = html.find("meta", itemprop="description")["content"]
        except TypeError:
            self.summary = None
            LOGGER.info("'%s' '%s' has no summary", self.__class__.__name__, self.name)

        self.description = str(html.find("div", id="profiledescription"))

        try:
            self.description = str(html.find("div", id="profiledescription"))
            self.plaintext = html.find("div", id="profiledescription").text
        except AttributeError:
            LOGGER.info(
                "'%s' '%s' has no extended description",
                self.__class__.__name__,
                self.name,
            )
            self.description = None
            self.plaintext = None

    def _get_suggestions(self, html: bs4.BeautifulSoup) -> List[Thumbnail]:
        """Hidden method used to get the list of suggestions on the page. As with most things, this list of suggestions
        will be a list of Thumbnail objects that can be parsed individually.

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The html page we are trying to parse the suggestions for

        Returns
        --------
        List[Thumbnail]
            The list of suggestions as thumbnails.
        """
        suggestions_raw = (
            html.find("span", string="You may also like")
            .parent.parent.parent.find("div", class_="table")
            .find_all("div", recursive=False)
        )
        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = get_page_type(link["href"])
                suggestion = Thumbnail(
                    name=link["title"],
                    url=link["href"],
                    image=link.img["src"],
                    type=suggestion_type,
                )
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def _get_games(self, html: bs4.BeautifulSoup) -> List[Thumbnail]:
        """Used both for Teams and Engines, returns a list of games  present on the page
        as Thumbnail objects.

        Parameters
        ----------
        html : bs4.BeautifulSoup
            The html to extract the list of games from

        Returns
        -------
        List[Thumbnail]
            The list of games on the page as Thumbnail objects.
        """
        games_raw = html.find(string="Games").parent.parent.parent.parent.find_all(
            class_="row rowcontent clear"
        )
        games = []
        for x in games_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            game = Thumbnail(
                name=link.string,
                url=link["href"],
                image=image_url,
                type=ThumbnailType.game,
            )
            games.append(game)

        return games

    def _get_files(self, html: bs4.BeautifulSoup) -> List[Thumbnail]:
        """Cache the files present on the page. Up to 5 files might be present

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The page to cache the files from

        Returns
        -------
        List[Thumbnail]
            The list of file like thumbnails
        """

        files_raw = html.find(string="Files").parent.parent.parent.parent.find_all(
            class_="row rowcontent clear"
        )
        files = []
        for x in files_raw:
            link = x.find("div", class_="content").h4.a
            try:
                image_url = link.parent.parent.parent.find("img")["src"]
            except TypeError:
                image_url = None

            file = Thumbnail(
                name=link.string,
                url=link["href"],
                image=image_url,
                type=ThumbnailType.file,
            )
            files.append(file)

        return files

    def _get_engines(self, html):
        """Hidden method to get the engines showed currently on the page as a list of engine like thumbnails. Takes
        an entire page of html and sorts it out

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The page to cache the engines from

        Returns
        -------
        List[Thumbnail]
            The list of engine like thumbnail objects
        """
        engines_raw = html.find(string="Engines").parent.parent.parent.parent.find_all(
            class_="row rowcontent clear"
        )
        engines = []
        for x in engines_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            engine = Thumbnail(
                name=link.string,
                url=link["href"],
                image=image_url,
                type=ThumbnailType.engine,
            )
            engines.append(engine)

        return engines

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"


class HardwareSoftwareMetaClass(
    BaseMetaClass, SharedMethodsMixin, RSSFeedMixin, GetWatchersMixin
):
    """Shared class for Hardware and Software

    Attributes
    -----------
    description : str
        Description of the page
    profile : Profile
        The page's profile
    stats : Statistics
        The page's stats
    rating : float
        The rating of the item
    articles : List[Thumbnail]
        List of article type thumbnails from the recommended articles
    article : PartialArticle
        The partial article presented on the front page
    tags : Dict{str : str}
        Dict of tags with the name as the key and the url as the value
    medias : List[Thumbnail]
        list of thumbnails representing all the combined media objects of a page (videos and images)
    suggestions : List[Thumbnail]
        list of suggested software/hardware type thumbnails
    """

    def __init__(self, html):
        super().__init__(html)
        try:
            self.description = html.find("div", id="profiledescription").p.string
        except AttributeError:
            self.description = html.find("p", itemprop="description").string

        self.profile = Profile(html)

        try:
            self.stats = Statistics(html)
        except AttributeError:
            LOGGER.info("Entity '%s' has no stats (idk why, ask moddb)", self.name)
            self.stats = None

        try:
            self.rating = float(
                html.find("div", class_="score").find("meta", itemprop="ratingValue")[
                    "content"
                ]
            )
        except AttributeError:
            self.rating = 0.0
            LOGGER.info("'%s' '%s' is not rated", self.profile.category.name, self.name)

        try:
            self._review_hash = html.find("form", class_="ratingform").find(
                "input", {"name": "hash"}
            )["value"]
        except AttributeError:
            self._review_hash = None

        articles_raw = None
        try:
            articles_raw = html.find(
                "span", string="Related Articles"
            ).parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [
                Thumbnail(
                    name=x.a["title"],
                    url=x.a["href"],
                    image=x.a.img["src"] if x.a.img else None,
                    summary=x.find("p").string,
                    date=x.find("time")["datetime"],
                    type=ThumbnailType.article,
                )
                for x in thumbnails
            ]
        except AttributeError:
            LOGGER.info(
                "'%s' '%s' has no article suggestions",
                self.profile.category.name,
                self.name,
            )
            self.articles = []

        if articles_raw:
            self.article = PartialArticle(articles_raw)
        else:
            self.article = None
            LOGGER.info(
                "'%s' '%s' has no front page article",
                self.profile.category.name,
                self.name,
            )

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {
                x.string: join(x["href"]) for x in raw_tags if x.string is not None
            }
        except AttributeError:
            self.tags = {}
            LOGGER.info("Hardware '%s' has no tags", self.name)

        self.medias = self._get_media(1, html=html)

        try:
            t = ThumbnailType[self.__class__.__name__.lower()]
            suggestions = html.find(
                "span", string="You may also like"
            ).parent.parent.parent.find_all("a", class_="image")
            self.suggestions = [
                Thumbnail(url=x["href"], name=x["title"], type=t, image=x.img["src"])
                for x in suggestions
            ]
        except AttributeError:
            LOGGER.info(
                "'%s' '%s' has no suggestions", self.__class__.__name__, self.name
            )
