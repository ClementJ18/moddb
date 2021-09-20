from .boxes import CommentList, Comment, Thumbnail, MemberProfile, MemberStatistics, \
                   Profile, Statistics, Style, PartialArticle, Option, PlatformStatistics, \
                   MissingComment, ResultList
from .enums import ThumbnailType, SearchCategory, TimeFrame, FileCategory, AddonCategory, \
                   MediaCategory, JobSkill, ArticleCategory, Difficulty, TutorialCategory, Licence, \
                   Status, PlayerStyle, Scope, Theme, HardwareCategory, SoftwareCategory, Genre, \
                   Membership, GroupCategory, RSSType
from .utils import get_page, join, LOGGER, get_date, get_views, get_type, concat_docs, Object, request, \
                   get_type_from, get_page_number

import re
import bs4
import json
import datetime
import feedparser
from typing import List, Tuple, Union

__all__ = ['Mod', 'Game', 'Engine', 'File', 'Addon', 'Media', 'Article',
           'Team', 'Group', 'Job', 'Blog', 'Member', 'FrontPage', 'Review',
           'Platform', 'Poll', 'Software', 'Hardware']

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
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
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
            self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", class_="reporticon")["href"])[1])
        except TypeError:
            self.id = None
            LOGGER.info("'%s' '%s' has no id", self.__class__.__name__, self.name)

        try:
            self.url = html.find("meta", property="og:url")["content"]
        except TypeError:
            self.url = join(html.find("a", string=self.name)["href"])

        self.name_id = self.url.split("/")[-1]

        try:
            self.report = join(html.find("a", string="Report")["href"])
        except TypeError:
            self.report = None
            LOGGER.info("'%s' '%s' cannot be reported", self.__class__.__name__, self.name)

        self.comments = self._get_comments(html)

        self._html = html

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

    def _get_comments(self, html : bs4.BeautifulSoup) -> CommentList:
        """Extracts the comments from an html page and adds them to a CommentList. In addition
        this method also adds them to the comments children as need be.

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The html containing the comments
        """
        page, max_page = get_page_number(html)

        comments = []
        comments_raw = html.find_all("div", class_="row", id=True)
        for raw in comments_raw:
            comment = Comment(raw)
            comment._url = f"{self.url}/page/{page}"
            if comment.position == 1:
                try:
                    comments[-1].children.append(comment)
                except IndexError:
                    comment.append(MissingComment(0))
                    comments[-1].children.append(comment)
            elif comment.position == 2:
                try:
                    comments[-1].children[-1].children.append(comment)
                except IndexError:
                    comments[-1].children.append(MissingComment(1))
                    comments[-1].children[-1].children.append(comment)
            else:
                comments.append(comment)

        return CommentList(
            results=comments, 
            page=page,
            max_page=max_page,
            action=self._get_comments_from_url,
            url=f"{self.url}/page/{page}",
        )

    def _get(self, url : str, *, params : dict = {}) -> ResultList:
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
        List[Thumbnail]
            The list of objects present on the page as a list of thumbnails.
        """
        html = get_page(url, params=params)
        try:
            table = html.find("form", attrs={'name': "filterform"}).parent.find("div", class_="table")
        except AttributeError:
            table = None

        if table is None:
            return []

        objects_raw = table.find_all("div", recursive=False)[1:]
        objects = []
        for obj in objects_raw:
            date = obj.find("time")
            summary = obj.find("p")
            thumbnail = Thumbnail(
                name=obj.a["title"], 
                url=obj.a["href"], 
                image=obj.a.img["src"], 
                type=get_type_from(join(obj.a["href"])), 
                summary=summary.string if summary else None, 
                date=get_date(date["datetime"]) if date else None
            )
            objects.append(thumbnail)

        page, max_page = get_page_number(html)

        return ResultList(
            results=objects, 
            params=params, 
            url=url, 
            action=self._get, 
            page=page, 
            max_page=max_page
        )

    def _get_media(self, index : int, *, html) -> List[Thumbnail]:
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
        return [Thumbnail(name=re.search(name_finder, match[0])[1], url=match[0], type=ThumbnailType.media, image=match[1]) for match in matches]

    def _get_comments_from_url(self, url, *, show_deleted = False):
        """Extra method so we can get comments from a ResultList"""
        params = {
            "deleted" : "t" if show_deleted else None
        }
        return self._get_comments(get_page(url, params=params))

    def get_comments(self, index : int = 1, *, show_deleted = False) -> CommentList:
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
        params = {
            "deleted" : "t" if show_deleted else None
        }

        return self._get_comments(get_page(f"{self.url}/page/{index}", params=params))

class GetGamesMixin:
    """Abstract class containing the get_games method"""
    def get_games(self, index : int = 1, *,  query : str = None, status : Status = None,
        genre : Genre = None, theme : Theme = None, scope : Scope = None, players : PlayerStyle = None,
        timeframe : TimeFrame = None, sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of games for the model. Each page will yield up to 30 games.

        Parameters
        -----------
        index : Optional[int]
            The page number to get the games for.
        query : Optional[str]
            The text to look for in the game names.
        status : Optional[Status]
            The status of the game (unreleased, released, early access, ect...)
        genre : Optional[Genre]
            The genre of the game (fps, tower defense)
        theme : Optional[Theme]
            The theme of the game (fantasy, action)
        scope : Optional[Scope]
            The scope of the game (AAA, indie)
        players : Optional[PlayerStyle]
            Player styles of the game (co-op, singleplayer)
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            List of game like thumbnails that can be parsed individually.
        """
        params = {
            "filter": "t",
            "kw": query,
            "released": status.value if status else None,
            "genre": genre.value if genre else None,
            "theme": theme.value if theme else None,
            "indie": scope.value if scope else None,
            "players": players.value if players else None,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/games/page/{index}", params=params)

class GetModsMixin:
    """Abstract class containing the get_mod method"""
    def get_mods(self, index : int = 1, *,  query : str = None, status : Status = None,
        genre : Genre = None, theme : Theme = None, players : PlayerStyle = None,
        timeframe : TimeFrame = None, game : Union['Game', Object] = None,
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of mods for the game. Each page will yield up to 30 mods. 
        
        Parameters
        -----------
        index : int
            The page number to get the mods from.
        query : Optional[str]
            The text to look for in the mod names.
        status : Optional[Status]
            The status of the mod (unreleased, released, early access, ect...)
        genre : Optional[Genre]
            The genre of the mod (fps, tower defense)
        theme : Optional[Theme]
            The theme of the mod (fantasy, action)
        players : Optional[PlayerStyle]
            Player styles of the mod (co-op, singleplayer)
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        game : Union[mod, Object]
            An mod object or an object with an id attribute which represents the
            mod the mod belongs to.
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            The list of mods type thumbnails parsed from the game
        """
        params = {
            "filter": "t",
            "kw": query,
            "released": status.value if status else None,
            "genre": genre.value if genre else None,
            "theme": theme.value if theme else None,
            "players": players.value if players else None,
            "timeframe": timeframe.value if timeframe else None,
            "game": game.id if game else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/mods/page/{index}", params=params)

class GetEnginesMixin:
    """Abstract class containing the get_engines method"""
    def get_engines(self, index : int = 1, *, query : str = None, status : Status = None, 
        licence : Licence = None, timeframe : TimeFrame = None,
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of engines for the game. Each page will yield up to 30 engines. 
        
        Parameters
        -----------
        index : int
            The page number to get the engines from.
        query : Optional[str]
            The text to look for in the engine names.
        status : Optional[Status]
            The status of the game (unreleased, released, early access, ect...)
        licence : Optional[Licence]
            The licence of the engine (open source, proprietary, ect...)
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results
        Returns
        --------
        ResultList[Thumbnail]
            The list of engine type thumbnails parsed from the game
        """
        params = {
            "filter": "t",
            "kw": query,
            "released": status.value if status else None,
            "licence": licence.value if licence else None,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/engines/page/{index}", params=params)

class SharedMethodsMixin:
    """Abstract class that implements a certain amount of top level methods shared between Pages
    and Hardware"""
    def get_reviews(self, index : int = 1, *, query : str = None, rating : int = None, 
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of reviews for the page. Each page will yield up to 10 reviews. 

        Parameters
        -----------
        index : Optional[int]
            The page number to get the reviews from.
        query : Optional[str]
            The string to look for in the review, optional.
        rating : Optiona[int]
            A number between 1 and 10 to get the ratings
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Review]
            The list of reviews parsed from the page
        """
        params = {
            'filter': "t", 
            'kw': query, 
            'rating': rating, 
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get_reviews(f"{self.url}/reviews/page/{index}", params=params)

    def _get_reviews(self, url, *, params):
        """Backend class so we can use it with ResultList"""
        html = get_page(url, params=params)

        try:
            table = html.find("form", attrs={'name': "filterform"}).parent.find("div", class_="table")
        except AttributeError:
            table = None

        if table is None:
            return []

        raw_reviews = table.find_all("div", recursive=False)[2:]
        reviews = []
        e = 0
        #This is very hacky because a page of reviews is actually a list of review titles and review contents
        #I'm not fucking with you, its a list of divs which go [Div[Title of review one], Div[content of review one],
        #Div[Title of review two], Div[content of review two]] It's dumb as fuck and I hate it.
        for _ in range(len(raw_reviews)):
            try:
                review = raw_reviews[e]
            except IndexError:
                break

            try:
                text = raw_reviews[e+1]
            except IndexError:
                #some reviews don't have text, it's optional as long as you don't give lower than a three
                text = {"class": "None"}

            if "rowcontentnext" in text["class"]:
                e += 1
                review_obj = Review(review=review, text=text)
            else:
                review_obj = Review(review=review)

            reviews.append(review_obj)
            e += 1

        page, max_page = get_page_number(html)

        return ResultList(
            results=reviews,
            params=params,
            action=self._get_reviews,
            url=url,
            page=page,
            max_page=max_page
        )

    def get_articles(self, index : int = 1, *, query : str = None, category : ArticleCategory = None, 
        timeframe : TimeFrame = None, sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of articles for the page. Each page will yield up to 30 articles. 

        Parameters
        -----------
        index : Optional[int]
            The page number to get the articles from.
        query : Optional[str]
            The string query to search for in the article name, optional.
        category : Optional[ArticleCategory]
            Type enum defining what the article is, optional
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            The list of article type thumbnails parsed from the page
        """
        params = {
            "filter": "t", 
            "kw": query, 
            "type": category.value if category else None, 
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/articles/page/{index}", params=params)
        
    def get_files(self, index : int = 1, *, query : str = None, category : FileCategory = None, 
        addon_type : AddonCategory = None, timeframe : TimeFrame = None,
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of files for the page. Each page will yield up to 30 files. 

        Parameters
        -----------
        index : Optional[int]
            The page number to get the files from.
        query : Optional[str]
            The string query to search for in the file name, optional.
        category : [FileCategory]
            Type enum defining what the file is, optional
        addon_type : Optional[AddonCategory]
            Type enum defining what category the file is.
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            The list of file type thumbnails parsed from the page
        """
        params = {
            "filter": "t", 
            "kw": query, 
            "category": category.value if category else None,
            "categoryaddon": addon_type.value if addon_type else None,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/downloads/page/{index}", params=params)

    def get_images(self) -> List[Thumbnail]:
        """Get all the images a page has uploaded. Literally all of them. As thumbnails. ModDB's imagebox
        caches all the urls for images on the page so this grabs them all. Lists might be long, but this 
        is all the images. They can be invidually parsed to get full fledged media objects from them.

        Returns
        --------
        List[Thumbnail]
            The list of image type thumbnails parsed from the page
        """
        html = get_page(f"{self.url}/images")
        return self._get_media(1, html=html)
        

    def get_videos(self) -> List[Thumbnail]:
        """Get all the videos a page has uploaded. Literally all of them. As thumbnails. ModDB's imagebox
        caches all the urls for videos on the page so this grabs them all. Lists might be long, but this 
        is all the videos. They can be invidually parsed to get full fledged media objects from them.

        Returns
        --------
        List[Thumbnail]
            The list of video type thumbnails parsed from the page
        """
        html = get_page(f"{self.url}/videos")
        return self._get_media(2, html=html)

    def get_tutorials(self, index : int = 1, *, query : str = None, difficulty : Difficulty = None, 
        tutorial_type : TutorialCategory = None, sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of tutorial for the page. Each page will yield up to 30 tutorials. 

        Parameters
        -----------
        index : int
            The page number to get the tutorials from.
        query : str
            The string query to look for in the tutorial title, optional.
        difficulty : Difficulty
            Enum type representing the difficulty of the tutorial, optional.
        tutorial_type : TutorialCategory
            Enum type representing the theme/type/category of the tutorial, optional.
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            The list of article type thumbnails parsed from the page
        """
        params = {
            "filter": "t", 
            "kw": query, 
            "subtype": tutorial_type.value if tutorial_type else None, 
            "meta": difficulty.value if difficulty else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/tutorials/page/{index}", params=params)

class GetSoftwareHardwareMixin:
    """Abstrac class implementing get_software and get_hardware"""
    def get_hardware(self, index : int = 1, *, query : str = None, status : Status = None,
        category : HardwareCategory = None, timeframe : TimeFrame = None,
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of hardware for the platform. Each page will yield up to 30 hardware.

        Parameters
        -----------
        index : Optional[int]
            The page number to get the hardware for.
        query : Optional[str]
            The text to look for in the hardware's names
        status : Optional[Status]
            Status of the hardware (released, unreleased, early access...)
        category : Optional[HardwareCategory]
            Category of the hardware (headset, controller, ect...)
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by

        Returns
        --------
        ResultList[Thumbnail]
            List of hardware like thumbnails that can be parsed individually.
        """
        params = {
            "filter": "t", 
            "kw": query, 
            "released": status.value if status else None,
            "category": category.value if category else None,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/hardware/page/{index}", params=params)

    def get_software(self, index : int = 1, *, query : str = None, status : Status = None,
        category : SoftwareCategory = None, timeframe : TimeFrame = None,
        sort : Tuple[str, str] = None) -> ResultList:
        """Get a page of software for the platform. Each page will yield up to 30 software.

        Parameters
        -----------
        index : int
            The page number to get the software for.
        query : Optional[str]
            The text to look for in the hardware's names
        status : Optional[Status]
            Status of the hardware (released, unreleased, early access...)
        category : Optional[SoftwareCategory]
            Category of the hardware (headset, controller, ect...)
        timeframe : Optional[TimeFrame]
            The time period this was released in (last 24hr, last week, last month)
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by

        Returns
        --------
        ResultList[Thumbnail]
            List of software like thumbnails that can be parsed individually.
        """
        params = {
            "filter": "t", 
            "kw": query, 
            "released": status.value if status else None,
            "category": category.value if category else None,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f'{sort[0]}-{sort[1]}' if sort else None
        }

        return self._get(f"{self.url}/software/page/{index}", params=params)

class RSSFeedMixin:
    def rss(self, type : RSSType, *, parse_feed = False):
        """Get the RSS feed url for the page depending on which feed type you want

        Parameters
        -----------
        type : RSSType
            The type of feed you desire to get
        parse_feed : Optional[bool]:
            Set to true if you want the library to parse the rss feed for you and return the entries as a dict
            rather than returning the url for the rss feed.

        Returns
        --------
        str
            URL for the feed type
        """
        url = f'https://rss.moddb.com/{self._type.name}/{self.name_id}/{type.name}/feed/rss.xml'    
        
        if parse_feed:
            return feedparser.parse(request(url).text)

        return url 

class PageMetaClass(BaseMetaClass, SharedMethodsMixin, RSSFeedMixin):
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
    def __init__(self, html : bs4.BeautifulSoup, page_type : SearchCategory):
        super().__init__(html)
        self._type = page_type

        #boxes
        if page_type != SearchCategory.members:
            self.profile = Profile(html)
            self.stats = Statistics(html)
            if page_type != SearchCategory.engines:
                self.style = Style(html)

            #thumbnails
            self.suggestions = self._get_suggestions(html)

            #misc
            try:
                self.embed = html.find("input", type="text", class_="text textembed")["value"]
            except TypeError:
                self.embed = str(html.find_all("textarea")[1].a)
       
        try:
            self.files = self._get_files(html)
        except AttributeError:
            LOGGER.info("'%s' '%s' has no files", self.__class__.__name__, self.name)
            self.files = []

        articles_raw = None
        try:
            raw = html.find("span", string="Articles") or html.find("span", string="Related Articles")
            articles_raw = raw.parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"] if x.a.img else None, summary=x.find("p").string, date=x.find("time")["datetime"], type=ThumbnailType.article) for x in thumbnails]
        except AttributeError:
            LOGGER.info("'%s' '%s' has no article suggestions", self.__class__.__name__, self.name)
            self.articles = []

        #main page article
        if articles_raw:
            self.article = PartialArticle(articles_raw)
        else:
            self.article = None
            LOGGER.info("'%s' '%s' has no front page article", self.__class__.__name__, self.name)

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("'%s' '%s' has no tags", self.__class__.__name__, self.name)

        #imagebox
        try:
            imagebox = html.find("ul", id="imagebox").find_all("li")[1:-2]
            self.imagebox = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], type=ThumbnailType(get_type(x.a.img))) for x in imagebox if x.a]
        except (AttributeError, TypeError):
            LOGGER.info("'%s' '%s' has no images", self.__class__.__name__, self.name)
            self.imagebox = []

        try:
            self.rating = float(html.find("div", class_="score").find("meta", itemprop="ratingValue")["content"])
        except AttributeError:
            self.rating = 0.0
            LOGGER.info("'%s' '%s' is not rated", self.__class__.__name__, self.name)

        try:
            self._review_hash = html.find("form", class_="ratingform").find("input", {"name": "hash"})["value"]
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
            LOGGER.info("'%s' '%s' has no extended description")
            self.description = None
            self.plaintext = None

    def _get_suggestions(self, html : bs4.BeautifulSoup) -> List[Thumbnail]:
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
        suggestions_raw = html.find("span", string="You may also like").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = get_type_from(link["href"])
                suggestion = Thumbnail(name=link["title"], url=link["href"], image=link.img["src"], type=suggestion_type)
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def _get_games(self, html : bs4.BeautifulSoup) -> List[Thumbnail]:
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
        games_raw = html.find(string="Games").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        games = []
        for x in games_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            game = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.game)
            games.append(game)

        return games

    def _get_files(self, html : bs4.BeautifulSoup) -> List[Thumbnail]:
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

        files_raw = html.find(string="Files").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        files = []
        for x in files_raw:
            link = x.find("div", class_="content").h4.a
            try:
                image_url = link.parent.parent.parent.find("img")["src"]
            except TypeError:
                image_url = None
                
            file = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.file)
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
        engines_raw = html.find(string="Engines").parent.parent.parent.parent.find_all(class_="row rowcontent clear")
        engines = []
        for x in engines_raw:
            link = x.find("div", class_="content").h4.a
            image_url = link.parent.parent.parent.find("img")["src"]
            engine = Thumbnail(name=link.string, url=link["href"], image=image_url, type=ThumbnailType.engine)
            engines.append(engine)

        return engines

    def get_addons(self, index : int = 1, *, query : str = None, addon_type : AddonCategory = None,
        timeframe : TimeFrame = None, licence : Licence = None) -> ResultList:
        """Get a page of addons for the page. Each page will yield up to 30 addons. 

        Parameters
        -----------
        index : int
            The page number to get the addons from.
        query : str
            The string query to search for in the addon name, optional.
        addon_type : AddonCategory
            Type enum defining what category the file is.
        timeframe : TimeFrame
            Time frame of when the file was added, optional
        licence : Licence
            The licence for the addon, optional

        Returns
        --------
        ResultList[Thumbnail]
            The list of addon type thumbnails parsed from the page
        """
        params = {
            "filter": "t",
            "kw": query,
            "category": addon_type.value if addon_type else None,
            "timeframe": timeframe.value if timeframe else None,
            "licence": licence.value if licence else None
        }
        return self._get(f"{self.url}/addons/page/{index}", params=params)

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"

@concat_docs
class Mod(PageMetaClass):
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
    def __init__(self, html : bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.mods)

@concat_docs
class Game(PageMetaClass, GetModsMixin):
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
    def __init__(self, html : bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.games)

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
    def __init__(self, html : bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.engines)
        delattr(self, "files")

        try:
            self.games = self._get_games(html)
        except AttributeError:
            LOGGER.info("Engine '%s' has no games", self.name)
            self.games = []

@concat_docs
class File(BaseMetaClass):
    """An oject representing a file on ModDB, a file is something posted by the page owner which is directly linked 
    to the page. It is endorsed by the page owner and they should do everythign they can to make sure that it is safe.
    As compared to an addon that may be added by fans to the page and that are files meant to work with the page but
    that are not directly related to the page. E.x the file of a mod page would be the mod files used to install the
    mod whereas an addon could be something like a fan-made texture pack for the mod or a map.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    category  : :class:`.FileCategory`
        The type of file (audio, video, demo, full version....)
    categoryaddon : :class:`.AddonCategory`
        The type of addon (map, textures, ect...)
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the file belongs to.
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
        * **date** - order by upload date, asc is most recent first, desc is oldest first

    Attributes
    -----------
    filename : str
        The name of the file
    hash : str
        The MD5 hash of the file
    name : str
        The name of the page
    size : int
        the file size in bytes
    today : int
        The number of downloads today
    downloads : int
        The total number of times this file has been downloaded
    category : FileCategory
        The category of the file
    author : Thumbnail
        A member type thumbnail of the member who uploaded the file
    date : datetime.datetime
        The date the file was uploaded
    button : str
        html code for the embed button
    widget : str
        html code for the embed widget
    description : str
        Description of the file, as written by the author
    preview : str
        URL of the preview image for the file
    """
    def __init__(self, html : bs4.BeautifulSoup):
        if html.find("span", string="File Deleted", class_="heading"):
            raise ValueError("This file has been removed")

        info = html.find("div", class_="table tablemenu")
        file = {x.string.lower() : x.parent.span.string.strip() for x in info.find_all("h5", string=("Filename", "Size", "MD5 Hash"))}
        self.name = html.find("a", title="Report").parent.parent.find("span", class_="heading").string
        self.filename = file["filename"]
        super().__init__(html)

        self.hash = file["md5 hash"]
        self.size = int(re.sub(r"[(),bytes]", "", file["size"].split(" ")[1]))

        downloads = html.find("h5", string="Downloads").parent.a.string
        self.today = int(re.sub(r"[(),today]", "", downloads.split(" ")[1]))
        self.downloads = int(downloads.split(" ")[0].replace(",", ""))

        try:
            self.category = FileCategory(int(info.find("h5", string="Category").parent.a["href"].split("=")[-1]))
        except ValueError:
            self.category = AddonCategory(int(info.find("h5", string="Category").parent.a["href"].split("=")[-1]))
        
        uploader = info.find("h5", string="Uploader").parent.a
        self.author = Thumbnail(url=uploader["href"], name=uploader.string, type=ThumbnailType.member)

        self.date = get_date(info.find("h5", string="Added").parent.span.time["datetime"])
        self.button = info.find("h5", string="Embed Button").parent.span.input["value"]
        self.widget = info.find("h5", string="Embed Widget").parent.span.input["value"]

        self.description = html.find("p", id="downloadsummary").string

        self.preview = html.find_all("img", src=True)[0]["src"]

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name} type={self.category.name}>"

    def save(self, path = None): 
        """Save the file to a location.

        Parameters
        -----------
        path : Optional[str]
            Path to the location you wish to save the file at. If none is provided
            it will save in the current working directory.

        """
        download = get_page(f"https://www.moddb.com/downloads/start/{self.id}")
        mirror = join(download.find("a", string=f"download {self.filename}")["href"])
        file = request(mirror)
        path = f"{path}/{self.filename}" if path else self.filename
        with open(path, "wb") as f:
            f.write(file.content)

@concat_docs
class Addon(File):
    """Object representing an addon. Seemingly the only difference between an addon and a file is in
    the semantics. A file often represents something official released by the page, e.g. the mod installation
    or an official guide where as addons are often fan made and might not be directly endorsed by the page owners
    even if it is allowed. They literally add on to the page's content without becoming part of it. There is a slight
    difference in their profiles but nothing beyond that.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    categoryaddon : :class:`.AddonCategory`
        The type of addon (map, textures, ect...)
    licence : :class:`.Licence`
        The licence of the addon
    game : Union[:class:`.Game`, :class:`.Object`]
        An game object or an object with an id attribute which represents the
        game the addon belongs to.
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
        * **licence** - order based on licence
        * **date** - order by upload date, asc is most recent first, desc is oldest first


    """
    pass

@concat_docs
class Media(BaseMetaClass):
    """Represents an image, audio file or video file on 

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    -----------
    sitearea : :class:`.Category`
        The type of model the media belongs to. Category.downloads is not valid for this.

    Sorting
    --------
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **id** - order by upload date, asc is most recent first, desc is oldest first

        Exclusive to videos and audios
        * **duration** - order by duration, asc is shortest to longest, desc is longest first

    Attributes
    -----------
    date : datetime.datetime
        The date the media was uploaded
    name : str
        The name of the media
    author : Thumbnail
        Member type thumbnail of the media uploader
    duration : datetime.timedelta
        Duration of the media in seconds, 0 if it's an image
    size : int
        Size of the files in bytes
    views : int
        Total amount of views
    today : int
        Amount of views today
    filename : str
        The name of the file for the media
    fileurl : str
        The url of the file for the media
    category : MediaCategory
        Whether the media is an image, a video or an audio
    description : str
        The description of the file as given by the file uploader.
    """
    def __init__(self, html : bs4.BeautifulSoup):
        try:
            self.name = html.find("meta", itemprop="name")["content"]
        except TypeError:
            self.name = html.find("img", id="mediaimage")["title"]
            
        super().__init__(html)
        medias = html.find_all("h5", string=("Date", "By", "Duration", "Size", "Views", "Filename"))
        raw_media = {media.string.lower() : media.parent for media in medias}
        
        self.date = get_date(raw_media["date"].span.time["datetime"])

        author = raw_media["by"].span.a
        self.author = Thumbnail(url=author["href"], name=author.string.strip(), type=ThumbnailType.member)

        if "duration" in raw_media:
            duration = raw_media["duration"].span.time.string.strip().split(":")
            duration.reverse()
            times = ["seconds", "minutes", "hours"]
            self.duration = datetime.timedelta(**{times[duration.index(x)] : int(x) for x in duration})
        else:
            self.duration = 0

        if "size" in raw_media:
            self.size = tuple(raw_media["size"].span.string.strip().split("×"))

        self.views, self.today = get_views(raw_media["views"].a.string)

        if "size" in raw_media and "duration" in raw_media:
            self.category = MediaCategory.video
            self.fileurl = html.find("meta", property="og:image")["content"][:-4]
        elif "size" in raw_media:
            self.category = MediaCategory.image
            self.fileurl = html.find("meta", property="og:image")["content"]
        else:
            self.category = MediaCategory.audio
            self.fileurl = html.find("video", id="mediaplayer").find("source")["src"]

        if "filename" in raw_media:
            self.filename = raw_media["filename"].span.string.strip()
        else:
            self.filename = self.fileurl.split("/")[-1]

        self.description = html.find("meta", {"name":"description"})["content"]

    def __repr__(self):
        return f"<Media name={self.name} type={self.type.name}>"

    def save(self, path = None): 
        """Save the media to a location.

        Parameters
        -----------
        path : Optional[str]
            Path to the location you wish to save the file at. If none is provided
            it will save in the current working directory.

        """
        file = request(self.fileurl)
        path = f"{path}/{self.filename}" if path else self.filename
        with open(path, "wb") as f:
            f.write(file.content)

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
    def __init__(self, html : bs4.BeautifulSoup):
        try:
            self.name = html.find("span", itemprop="headline").string
        except AttributeError:
            self.name = html.find("span", itemprop="heading").string

        super().__init__(html)

        raw_type = html.find("h5", string="Browse").parent.span.a.string
        self.category = ArticleCategory[raw_type.lower()]

        try:
            raw = html.find("span", string=raw_type[0:-1]).parent.parent.parent.find("div", class_="table tablemenu")
        except AttributeError:
            raw = html.find("span", string=raw_type).parent.parent.parent.find("div", class_="table tablemenu")

        try:
            self.profile = Profile(html)
        except AttributeError:
            LOGGER.info("'%s' has no profile", self.name)
            self.profile = None

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
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
class Group(PageMetaClass):
    """This object represents the group model of  Certain attributes can be None if the group
    has been set to private. If you wish to see a group you have access to then you can login with the
    login 

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    subscriptions : :class:`.Membership`
        The subscription system of the group (private, invitation)
    category : :class:`.GroupCategory`
        The category of the group (funny, literature)

    Sorting
    --------
        * **id** - order group by date, asc is most recent first, desc is oldest first
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **membercount** - order by number of members, asc is most members first, desc is lest member first

    Attributes
    -----------
    name : str
        The name of the group
    private : bool
        Whether or not the group is private
    profile : Profile
        The profile object for the group
    stats : Statistics
        The stats of the Group
    tags : dict{str, str}
        A dictionnary of tags where the key is the tag name and the value is the tag url
    embed : str
        The html for athe group embed
    medias : List[Thumbnail]
        A list of media like thumbnail objects representing all the images, videos and audio
        clips that a group has published.
    suggestions : List[Thumbnail]
        A list of group like thumbnail objects representing the suggestions made by moddb to
        members visiting this group
    articles : List[Thumbnail]
        A list of article like thumbnail objects representing some of the articles published
        by the group
    description : str
        The plaintext description of the group
    """
    def __init__(self, html : bs4.BeautifulSoup):
        self.name = html.find("div", class_="title").h2.a.string
        BaseMetaClass.__init__(self, html)
        self.private = False

        try:
            self.profile = Profile(html)
        except AttributeError:
            LOGGER.info("Entity '%s' has no profile (private)", self.name)
            self.profile = None
            self.private = True

        try:
            self.stats = Statistics(html)
        except AttributeError:
            LOGGER.info("Entity '%s' has no stats (private)", self.name)
            self.stats = None

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            LOGGER.info("Entity '%s' has no tags (private)", self.name)
            self.tags = {}

        try:
            self.embed = html.find("input", type="text", class_="text textembed")["value"]
        except TypeError:
            try:
                self.embed = str(html.find_all("textarea")[1].a)
            except IndexError:
                LOGGER.info("Group '%s' has no embed", self.name)
                self.embed = None

        self.suggestions = self._get_suggestions(html)

        try:
            articles_raw = html.find("span", string="Articles").parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear", recursive=False)
            self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"], summary=x.find("p").string, date=x.find("time")["datetime"], type=ThumbnailType.article) for x in thumbnails]
        except AttributeError:
            LOGGER.info("Group '%s' has no article suggestions", self.name)
            self.articles = []

        try:
            self.description = html.find("div", id="profiledescription").text
        except AttributeError:
            self.description = html.find("div", class_="column span-all").find("div", class_="tooltip").parent.text

        self.medias = self._get_media(2, html=html)

    def get_reviews(self, *args, **kwargs):
        """"""
        raise AttributeError(f"{self.__class__.__name__} has no 'get_reviews' attribute")

    def _get_suggestions(self, html : bs4.BeautifulSoup) -> List[Thumbnail]:
        """Hidden method used to get the list of suggestions on the page. As with most things, this list of suggestions
        will be a list of Thumbnail objects that can be parsed individually. Slightly modified to fit a group

        Parameters
        -----------
        html : bs4.BeautifulSoup
            The html page we are trying to parse the suggestions for

        Returns
        --------
        List[Thumbnail]
            The list of suggestions as thumbnails.
        """
        try:
            suggestions_raw = html.find("span", string=("You may also like", "Popular Articles")).parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
        except AttributeError:
            LOGGER.info("Group '%s' has no sidebar suggestions", self.name)
            return []

        suggestions = []
        for x in suggestions_raw:
            try:
                link = x.find("a", class_="image")
                suggestion_type = link["href"].split("/")[1].replace("s", "")
                suggestion = Thumbnail(name=link["title"], url=link["href"], image=link.img["src"], type=ThumbnailType[suggestion_type])
                suggestions.append(suggestion)
            except (AttributeError, TypeError):
                pass

        return suggestions

    def __repr__(self):
        return f"<Group name={self.name}>"

@concat_docs
class Team(Group, GetEnginesMixin, GetGamesMixin, GetModsMixin, GetSoftwareHardwareMixin):
    """A team is a group of people, which are the author of a game, a mod or an engine. A group has members which all
    have rights on those page. Like a member but instead of a single person authoring various mods and games it's several.

    Parameters
    ------------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    subscriptions : :class:`.Membership`
        The subscription system of the company (private, invitation)
    category : :class:`.TeamCategory`
        What does the team do (publisher, developer)

    Sorting
    --------
        * **id** - order by creation, desc is most recent first, asc is oldest first
        * **ranktoday** - order by daily ranking, asc is highest ranked, desc is lowest rank
        * **visitstotal** - order by most views, asc is highest views, desc is lowest views
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **game** - order by game???
        * **dateup** - order by latest update, asc is most recent update first, desc is oldest update first

    Attributes
    -----------
    games : List[Thumbnail]
        A list of game like thumbnails that the team has authored.
    engines : List[Thumbnail]
        A list of engine like objects that the team has authored.     

    """
    def __init__(self, html : bs4.BeautifulSoup):
        super().__init__(html)
        try:
            self.games = self._get_games(html)
        except AttributeError:
            LOGGER.info("Team '%s' has no games", self.name)
            self.games = []

        try:
            self.engines = self._get_engines(html)
        except AttributeError:
            LOGGER.info("Team '%s' has no engines", self.name)
            self.engines = []
        try:
            mods = html.find("span", string="Popular Mods").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
            self.mods = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.mod, image=x.a.img["src"]) for x in mods]
        except AttributeError:
            LOGGER.info("Team '%s' has no mods", self.name)
            self.mods = []

@concat_docs
class Job:
    """Model representing a job proposed on ModDB
    
    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    skill : :class:`.JobSkill`
        The job skill looked for
    earn : :class:`.bool`
        Whether or not the job is paid

    Sorting
    --------
        * **location** - order by the location of the job
        * **name** - order alphabetically, asc is a-z, desc is z-a
        * **skill** - order by the skill required
        * **id** - order by upload date, asc is most recent, desc is oldest first

    Attributes
    -----------
    id : int
        id of the job
    name_id : str
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.
    author : Thumbnail
        A member like thumbnail representing the poster of the job. Can be none if they desire to remain private.
    paid : bool
        Whether or not the job is paid
    tags : dict{str : str}
        A dict of key-values pair where the key is the name of the tag and the value is the url.
    skill : JobSkill
        the skill demanded for the job
    location : str
        The location the job will be at
    name : str
        The name of the job
    text : str
        The description of the job
    related : List[Thumbnail]
        A list of team like thumbnails of companies related to the job poster

    """
    def __init__(self, html : bs4.BeautifulSoup):
        breadcrumb = json.loads(html.find("script", type="application/ld+json").string)["itemListElement"][-1]["Item"]
        self.name = breadcrumb["name"]
        self.url = breadcrumb["@id"]
        self.name_id = self.url.split("/")[0]
        self.text = html.find("div", id="articlecontent").text

        profile_raw = html.find("span", string="Jobs").parent.parent.parent.find("div", class_="table tablemenu")

        self.id = int(re.search(r"siteareaid=(\d*)", html.find("a", string="Report")["href"])[1])

        try:
            author = profile_raw.find("h5", string="Author").parent.span.a
            self.author = Thumbnail(url=author["href"], name=author.string, type=ThumbnailType.member)
        except AttributeError:
            LOGGER.info("Job '%s' has no author", self.name)
            self.author = None

        self.paid = profile_raw.find("h5", string="Paid").parent.a.string == "Yes"

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("'%s' '%s' has no tags", self.__class__.__name__, self.name)

        self.skill = JobSkill(int(profile_raw.find("h5", string="Skill").parent.span.a["href"][-1]))

        self.location = profile_raw.find("h5", string="Location").parent.span.string.strip()

        try:
            related = html.find("div", class_="tablerelated").find_all("a", class_="image")
            self.related = [Thumbnail(url=x["href"], name=x["title"], type=ThumbnailType.team) for x in related]
        except AttributeError:
            LOGGER.info("Job '%s' has no related companies", self.name)
            self.related = []

        self._html = html

    def __repr__(self):
        return f"<Job name={self.name}>"

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

@concat_docs
class Member(PageMetaClass, GetGamesMixin, GetModsMixin):
    """The object to represent an individual member on ModDB

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Sorting
    --------
    * **username** - sort alphabetically by username, asc is z-a and desc is a-z
    * **id** - sort by member creation date, asc is most recent, desc is oldest
    * **online** - sort by last online, asc is most recently seen online and desc is least recently

    Attributes
    -----------
    profile : MemberProfile
        Since member profile boxes have no overlap with other profiles, they are a separate object type
        but serve the same function of making the side box "Profile" into an object, except exclusively
        for a member page.
    stats : MemberStatistics
        Since member statistics have no overlap with regular statistic pages, they are a separate object type
        but serve the same function of making the side box "Statistics" into an object, but exclusively for
        the member page.
    description : str
        Description written on the member profile
    groups : List[Thumbnail]
        A list of group/team like thumbnail objects representing both the Teams the member is part of and the
        Groups the member is part of.
    blog : Blog
        The front page blog shown on the member page
    blogs : List[Thumbnail]
        A list of blog like thumbnails representing the blog suggestion of a member's frontpage
    friends : List[Thumnails]
        A list of member like thumbnails representing some of the friends shown on the member's front
        page
    """
    def __init__(self, html : bs4.BeautifulSoup):
        super().__init__(html, SearchCategory.members)
        try:
            self.profile = MemberProfile(html)
        except AttributeError:
            LOGGER.info("Member '%s' has no profile (private)", self.name)
            self.profile = None

        try:
            self.stats = MemberStatistics(html)
        except  AttributeError:
            LOGGER.info("Member '%s' has no stats (private)", self.name)
            self.stats = None

        try:
            self.description = html.find("div", id="profiledescription").p.string
        except AttributeError:
            LOGGER.info("Member '%s' has no description", self.name)
            self.description = None

        try:
            groups_raw = html.find("span", string="Groups").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-2]
            self.groups = [Thumbnail(name=div.a["title"], url=div.a["href"], type=ThumbnailType.group) for div in groups_raw]
        except AttributeError:
            LOGGER.info("Member '%s' doesn't have any groups", self.name)
            self.groups = []

        try:
            blogs_raw = html.find("span", string="My Blogs").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
            self.blog = Blog(heading=blogs_raw.pop(0), text=blogs_raw.pop(0))
        except (TypeError, AttributeError):
            self.blog = None
            LOGGER.info("Member '%s' has no front page blog", self.name)

        try:
            blogs_raw = html.find("span", string="My Blogs").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)
            self.blogs = [Thumbnail(name=blog.a.string, url=blog.a["href"], type=ThumbnailType.blog) for blog in blogs_raw[:-2]]
        except (TypeError, AttributeError):
            self.blogs = []
            LOGGER.info("Member '%s' has no blog suggestions", self.name)

        try:
            friends = html.find("div", class_="table tablerelated").find_all("div", recursive=False)[1:]
            self.friends = [Thumbnail(name=friend.a["title"], url=friend.a["href"], type=ThumbnailType.member) for friend in friends]
        except AttributeError:
            self.friends = []
            LOGGER.info("Member '%s' has no friends ;(", self.name)

    def __repr__(self):
        return f"<Member name={self.name} level={self.profile.level}>"

    def get_blogs(self, index : int = 1, *, query : str = None, timeframe : TimeFrame = None, 
                  sort : Tuple[str, str] = None) -> ResultList:
        """Search through a member's blogs one page at a time with certain filters.

        Parameters
        -----------
        index : int
            The page index you wish to get the blogs for, allows to hop around.
        timeframe : TimeFrame
            The date the blog was added, optional
        query : str
            The string to look for in the blog title, optional.
        sort : Tuple[str, str]
            The sorting tuple to sort by

        Returns
        --------
        ResultList[Blog]
            The list of blogs on this page. 
        """
        params = {
            "filter": "t",
            "kw": query,
            "timeframe": timeframe.value if timeframe else None,
            "sort": f"{sort[0]}-{sort[1]}" if sort else None
        }

        return self._get_blogs(f"{self.url}/blogs/page/{index}", params=params)

    def _get_blogs(self, url, *, params):
        """Backend class so we can use it with ResultList"""
        html = get_page(url, params=params)
        try:
            table = html.find("form", attrs={'name': "filterform"}).parent.find("div", class_="table")
        except AttributeError:
            table = None

        if table is None:
            return []

        raw_blogs = table.find_all("div", recursive=False)[2:]
        blogs = []
        e = 0
        for _ in range(len(raw_blogs)):
            try:
                heading = raw_blogs[e]
            except IndexError:
                break

            try:
                text = raw_blogs[e+1]
            except IndexError:
                text = {"class": None}

            blog_obj = Blog(heading=heading, text=text)
            blogs.append(blog_obj)
            e += 2

        page, max_page = get_page_number(html)

        return ResultList(
            results=blogs,
            params=params,
            url=url,
            action=self._get_blogs,
            page=page,
            max_page=max_page
        )

    def get_member_comments(self, index : int = 1, *, show_deleted : bool = False) -> CommentList:
        """Gets a page of all the comments a member has posted.
        
        Parameters
        -----------
        index : int
            The page number to get the comments from.
        show_deleted : Optional[bool]
            Pass true to show deleted user comments. Only works if it is a page
            you have permissions on.

        Returns
        --------
        CommentList[Comment]
            A list of the comments made by the user.

        """
        params = {
            "deleted" : "t" if show_deleted else None
        }

        html = get_page(f"{self.url}/comments/page/{index}", params=params)
        return self._get_comments(html)

    def get_friends(self, index : int = 1, *, username : str = None) -> ResultList:
        """Get a page of the friends of the member
    
        Parameters
        -----------
        index : int
            The page number to get the friends from.
        username : Optional[str]
            The username of the user you are looking for

        Returns
        --------
        ResultList[Thumbnail]
            A list of member like thumbnails of the member's friends
        """
        params = {
            "filter": "t",
            "username": username
        }

        return self._get(f"{self.url}/friends/page/{index}", params=params)

    def get_groups(self, index : int = 1, *, query : str = None, subscription : Membership = None,
        category : GroupCategory = None) -> ResultList:
        """Get a page of the groups and teams a member is part of.
        
        Parameters
        -----------
        index : int
            The page number to get the friends from.
        query : Optional[str]
            The text to look for in the group's name
        subscription : Optional[Membership]
            The membership rules
        category : Optional[GroupCategory]
            The category of groups to search for

        Returns
        --------
        ResultList[Thumbnail]
            A list of team/group like thumbnails the member is part of
        """
        params = {
            "filter": "t",
            "kw": query,
            "subscription": subscription.value if subscription else None,
            "category": category.value if category else None
        }

        return self._get(f"{self.url}/groups/page/{index}", params=params)

class FrontPage:
    """An object representing the front page of  More of less just a long suggestion of the hottest mods,
    games, articles and files of the moment

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Attributes
    -----------
    slider : List[Thumnail]
        A list of object like thumbnails presented by the slider present on
        the front page, this is a catered list of promoted content, can contain
        any type of object.
    articles : List[Thumbnail]
        A list of article like thumbnail objects representing the suggested
        articles on the front page.
    mods : List[Thumbnail]
        A list of mod like thumbnail objects representing the suggested
        mods on the front page.
    games : List[Thumbnail]
        A list of game like thumbnail objects representing the suggested
        games on the front page.
    files : List[Thumbnail]
        A list of file like thumbnail objects representing the suggested
        files on the front page.
    poll : Poll
        The current ongoing moddb poll. Currently cannot be voted on.

    """
    def __init__(self, html : bs4.BeautifulSoup):
        slider = html.find("div", class_="rotatorholder").find_all("div", class_="rotatorbox")
        self.slider = []
        for x in slider:
            name = x.a.find("h2")
            summary = x.a.find("p")

            image = re.search(r'\((.*)\)', x["style"])
            if image:
                image = image.group(1)
            else:
                try:
                    image = x["data-bg"]
                except KeyError:
                    image = None

            thumbnail = Thumbnail(
                name=name.string if name else None, 
                url=x.a["href"], 
                summary=summary.string if summary else None, 
                image=image, 
                type=get_type_from(x.a["href"])
            )

            self.slider.append(thumbnail)


        articles = html.find("span", string="Latest Articles").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.article, image=x.a.img["src"], summary=x.find("p").string, date=x.find("time")["datetime"]) for x in articles]

        mods = html.find("span", string="Popular Mods").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.mods = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.mod, image=x.a.img["src"]) for x in mods]

        games = html.find("span", string="Popular Games").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.games = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.game, image=x.a.img["src"]) for x in games]

        jobs = html.find("span", string="Jobs").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.jobs = [Thumbnail(name=x.find("a").string, url=join(x.find("a")["href"]), type=ThumbnailType.job) for x in jobs]

        files = html.find("span", string="Popular Files").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[1:]
        self.files = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.file, image=x.a.img["src"]) for x in files]

        self.poll = Poll(get_page(html.find("div", class_="poll").form["action"]))

        self._html = html

    def __repr__(self):
        return f"<FrontPage articles={len(self.articles)} mods={len(self.mods)} games={len(self.games)} files={len(self.files)}>"

@concat_docs
class Platform(BaseMetaClass, GetModsMixin, GetGamesMixin, GetEnginesMixin, GetSoftwareHardwareMixin):
    """Represents the platform supporting the game/engines. Game and engines may have mutiple platforms.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
    released : :class:`.Status`
        Current status of release (unreleased, early access, ect...)

    Sorting
    --------
        * **released** - when the object was released, asc is oldest, desc is most recent
        * **id** - when it was added to moddb, asc is oldest, desc is most recent
        * **porder** - what plaform it's on???
        * **company** - company that made it in alphabetical order


    Attributes
    -----------
    name : str
        The name of the platform
    name_id : str
        The name_id of the member, cannot be changed, it's a mix of the original username lowercased with
        spaces removed and shortened.
    id : int
        The moddb id of the platform
    url : str
        The url of the platform page
    description : str
        Description of the platform
    company : Thumbnail
        A team like thumbnail of the company.
    homepage : str
        Link to the homepage of the engine
    date : datetime.datetime
        Date the engine was published
    stats : PlatformStatistics
        Stat data on the platform
    share : dict{str : str}
        Share link of the platform with the name of the share as key and link of the share as url.
    comments : CommentList[Comment]
        Comments on this page
    games : List[Thumbnail]
        A list of games suggested on the platform main page.
    hardware : List[Thumbnail]
        A list of hardware suggested on the platform main page.
    software : List[Thumbnail]
        A list of software suggested on the platform main page.
    engines : List[Thumbnail]
        A list of engines suggested on the platform main page.
    mods : List[Thumbnail]
        A list of mods suggested on the platform main page.
    """
    def __init__(self, html):
        self.name = html.find("a", itemprop="mainEntityOfPage").string
        self.id = None

        self.url = join(html.find("a", itemprop="mainEntityOfPage")["href"])
        self.name_id = self.url.split("/")[0]
        try:
            self.description = html.find("div", id="profiledescription").p.string
        except AttributeError:
            self.description = html.find("p", itemprop="description").string

        try:
            company = html.find("h5", string="Company").parent.span.a
            self.company = Thumbnail(name=company.string, url=company["href"], type=ThumbnailType.team)
        except AttributeError:
            LOGGER.info("Platform '%s' has no company", self.name)
            self.company = None

        self.homepage = html.find("h5", string="Homepage").parent.span.a["href"]

        self.date = get_date(html.find("time", itemprop="releaseDate")["datetime"])

        self.stats = PlatformStatistics(html)

        try:
            share = html.find("h5", string="Share").parent.span.find_all("a")
            self.share = {
                "reddit": share[0]["href"],
                "mail": share[1]["href"],
                "twitter": share[2]["href"],
                "facebook": share[3]["href"]
            }
        except (AttributeError, IndexError):
            LOGGER.info("Something funky about share box of platform '%s'", self.name)
            self.share = None

        self.comments = self._get_comments(html)
        
        hardware = html.find("span", string=" Hardware").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.hardware = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.hardware, image=x.a.img["src"]) for x in hardware]

        software = html.find("span", string=" Software").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.software = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.software, image=x.a.img["src"]) for x in software]

        engines = html.find("span", string=" Engines").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.engines = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.engine, image=x.a.img["src"]) for x in engines]

        mods = html.find("span", string=" Mods").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.mods = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.mod, image=x.a.img["src"]) for x in mods]

        games = html.find("span", string=" Games").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
        self.games = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.game, image=x.a.img["src"]) for x in games]


    def __repr__(self):
        return f"<Platform name={self.name}>"

class HardwareSoftwareMetaClass(BaseMetaClass, SharedMethodsMixin, RSSFeedMixin):
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
        self.stats = Statistics(html)

        try:
            self.rating = float(html.find("div", class_="score").find("meta", itemprop="ratingValue")["content"])
        except AttributeError:
            self.rating = 0.0
            LOGGER.info("'%s' '%s' is not rated", self.profile.category.name, self.name)

        try:
            self._review_hash = html.find("form", class_="ratingform").find("input", {"name": "hash"})["value"]
        except AttributeError:
            self._review_hash = None

        articles_raw = None
        try:
            articles_raw = html.find("span", string="Related Articles").parent.parent.parent.find("div", class_="table")
            thumbnails = articles_raw.find_all("div", class_="row rowcontent clear")
            self.articles = [Thumbnail(name=x.a["title"], url=x.a["href"], image=x.a.img["src"] if x.a.img else None, summary=x.find("p").string, date=x.find("time")["datetime"], type=ThumbnailType.article) for x in thumbnails]
        except AttributeError:
            LOGGER.info("'%s' '%s' has no article suggestions", self.profile.category.name, self.name)
            self.articles = []

        if articles_raw:
            self.article = PartialArticle(articles_raw)
        else:
            self.article = None
            LOGGER.info("'%s' '%s' has no front page article", self.profile.category.name, self.name)

        try:
            raw_tags = html.find("form", attrs={"name": "tagsform"}).find_all("a")
            self.tags = {x.string : join(x["href"]) for x in raw_tags if x.string is not None}
        except AttributeError:
            self.tags = {}
            LOGGER.info("Hardware '%s' has no tags", self.name) 

        self.medias = self._get_media(1, html=html)

        try:
            t = ThumbnailType[self.__class__.__name__.lower()]
            suggestions = html.find("span", string="You may also like").parent.parent.parent.find_all("a", class_="image")
            self.suggestions = [Thumbnail(url=x["href"], name=x["title"], type=t, image=x.img["src"]) for x in suggestions]
        except AttributeError:
            LOGGER.info("'%s' '%s' has no suggestions", self.__class__.__name__, self.name)

@concat_docs
class Hardware(HardwareSoftwareMetaClass, GetGamesMixin, GetSoftwareHardwareMixin):
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
            hardware = html.find("span", string="Hardware").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
            self.hardware = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.hardware, image=x.a.img["src"]) for x in hardware]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no hardware", self.name)
            self.hardware = []

        try:
            software = html.find("span", string="Software").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
            self.software = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.software, image=x.a.img["src"]) for x in software]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no software", self.name)
            self.software = []

        try:
            games = html.find("span", string="Games").parent.parent.parent.find("div", class_="table").find_all("div", recursive=False)[:-1]
            self.games = [Thumbnail(name=x.a["title"], url=x.a["href"], type=ThumbnailType.game, image=x.a.img["src"]) for x in games]
        except AttributeError:
            LOGGER.info("Hardware '%s' has no games", self.name)
            self.games = []

        try:
            history = html.find("span", string="History").parent.parent.parent.find_all("a", class_="image")
            self.history = [Thumbnail(url=x["href"], name=x["title"], type=ThumbnailType.hardware, image=x.img["src"]) for x in history]
        except AttributeError:
            LOGGER.info("Harware '%s' has no history", self.name)
            self.history = []

        try:
            recommended = html.find("span", string="Recommended").parent.parent.parent.find_all("a", class_="image")
            self.recommended = [Thumbnail(url=x["href"], name=x["title"], type=ThumbnailType.hardware, image=x.img["src"]) for x in recommended]
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


@concat_docs
class Review:
    """Represents a review.

    Filtering
    -----------
    rating : int
        A value from 1 to 10 denoting the rating number you're looking for
    sitearea : Category
        The type of model the rating is for (mod, engine, game)

    Sorting
    --------
        * **ratingalt** - rating number, desc is biggest to lowest, asc is lowest to biggest
        * **memberipid** - sort reviewer account age, asc is oldest reviewer first
        * **positive** - how many people agree with it, desc is most to least people agreeing
        * **negative** - how many people disagree with it, desc is most to least people disagreeing
        * **id** - when it was added to moddb, asc is oldest, desc is most recent

    Attributes
    -----------
    id : int
        The review id
    text : str
        The contents of the review. Can be none if the member hasn't left any
    rating : int
        An int out of 10 representing the rating left with this review.
    author : Thumbnail
        A member like thumbnail of the member who left the review
    date : datetime.datetime
        Date and time of the review creation
    agree : str
            Link to agree with the review
    disagree : str
        Link to disagree with the review
    """
    def __init__(self, **attrs):
        text = attrs.get("text")
        if text:
            self.text = text.text
        else:
            self.text = None

        review = attrs.get("review")
        self.rating = int(review.span.string)

        try:
            strings = ("Agree", "Delete", "Disagree")
            self.id = int(re.findall(r"siteareaid=(\d*)", review.find("a", title=strings)["href"])[0])
        except TypeError:
            self.id = None

        try:
            self._hash = re.findall(r"hash=(.*)&", review.find("a", title="Delete")["href"])[0]
        except TypeError:
            self._hash = None

        author = review.div.a
        self.author = Thumbnail(url=author["href"], name=author.string.split(" ")[0], type=ThumbnailType.member)
        self.date = get_date(review.div.span.time["datetime"])

        try:
            self.agree = join(review.find("a", title="Agree")["href"])
            self.disagree = join(review.find("a", title="Disagree")["href"])
        except TypeError:
            self.agree = None
            self.disagree = None

    def __repr__(self):
        return f"<Review author={self.author.name} rating={self.rating}>"

@concat_docs
class Poll(BaseMetaClass):
    """Represents a poll. Cannot be voted for due to restrictions implemented by the website.

    Parameters
    -----------
    html : bs4.BeautifulSoup
        The html to parse. Allows for finer control.

    Filtering
    ----------
        month : Month
            The month the poll you're looking for should be from
        year : int
            A int representing a year between 2002 and now. Anything below or above 2002 will
            always return zero results.

    Sorting
    --------
        * **totalvotes** - how many people voted on the poll, desc is most to least
        * **name** - sort the poll alphabetically by name, asc is a-z
        * **date** - when it was added to moddb, asc is oldest, desc is most recent

    Attributes
    -----------
    question : str
        The question of the poll
    author : Thumbnail
        A member like thumbnail of the member who posted the poll, usually ModDB staff
    total : int
        The total number of votes that have been cast
    options : List[Option]
        The list of available options for the poll
    """
    def __init__(self, html):
        poll = html.find("div", class_="poll")
        self.question = poll.parent.parent.parent.find("div", class_="normalcorner").find("span", class_="heading").string
        self.name = self.question
        super().__init__(html)
        author = poll.find("p", class_="question").find("a")
        self.author = Thumbnail(name=author.string, url=author["href"], type=ThumbnailType.member)

        self.total = int(re.search(r"([\d,]*) votes", poll.find("p", class_="question").text)[1].replace(",", ""))

        percentage = poll.find_all("div", class_="barouter")
        rest = poll.find_all("p")[1:]

        self.options = []
        for index, _ in enumerate(percentage):
            raw = percentage[index].div.string.replace('%', '').replace('\xa0', '')
            percent = float(f"0.{raw}")
            text = re.sub(r"\([\d,]* vote(s)?\)", '', rest[index].text)
            votes = int(re.search(r"([\d,]*) vote(s)?", rest[index].span.string)[1].replace(',', ''))
            self.options.append(Option(text=text, votes=votes, percent=percent))

    def __repr__(self):
        return f"<Poll question={self.question}>"
