import json
from typing import Tuple, Union, List

from . import opinion

from ..utils import BASE_URL, get_page, Object, get_sitearea
from ..boxes import ResultList, Tag, Thumbnail
from ..enums import (
    Status,
    Genre,
    Theme,
    Scope,
    PlayerStyle,
    TimeFrame,
    Licence,
    ArticleCategory,
    FileCategory,
    AddonCategory,
    Difficulty,
    TutorialCategory,
    HardwareCategory,
    SoftwareCategory,
    RSSType,
)


class GetGamesMixin:
    """Abstract class containing the get_games method"""

    def get_games(
        self,
        index: int = 1,
        *,
        query: str = None,
        status: Status = None,
        genre: Genre = None,
        theme: Theme = None,
        scope: Scope = None,
        players: PlayerStyle = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/games/page/{index}", params=params)


class GetModsMixin:
    """Abstract class containing the get_mod method"""

    def get_mods(
        self,
        index: int = 1,
        *,
        query: str = None,
        status: Status = None,
        genre: Genre = None,
        theme: Theme = None,
        players: PlayerStyle = None,
        timeframe: TimeFrame = None,
        game: Union["Game", Object] = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/mods/page/{index}", params=params)


class GetEnginesMixin:
    """Abstract class containing the get_engines method"""

    def get_engines(
        self,
        index: int = 1,
        *,
        query: str = None,
        status: Status = None,
        licence: Licence = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/engines/page/{index}", params=params)


class SharedMethodsMixin:
    """Abstract class that implements a certain amount of top level methods shared between Pages
    and Hardware"""

    def get_reviews(
        self,
        index: int = 1,
        *,
        query: str = None,
        rating: int = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "filter": "t",
            "kw": query,
            "rating": rating,
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        base_url = f"{self.url}/reviews"
        url = f"{base_url}/page/{index}"
        html = get_page(url, params=params)
        results, current_page, total_pages, total_results = opinion.parse_reviews(html)

        return opinion.ReviewList(
            results=results,
            url=base_url,
            total_results=total_results,
            params=params,
            current_page=current_page,
            total_pages=total_pages,
        )

    def get_articles(
        self,
        index: int = 1,
        *,
        query: str = None,
        category: ArticleCategory = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/articles/page/{index}", params=params)

    def get_files(
        self,
        index: int = 1,
        *,
        query: str = None,
        category: FileCategory = None,
        addon_type: AddonCategory = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
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

    def get_tutorials(
        self,
        index: int = 1,
        *,
        query: str = None,
        difficulty: Difficulty = None,
        tutorial_type: TutorialCategory = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
        """Get a page of tutorial for the page. Each page will yield up to 30 tutorials.

        Parameters
        -----------
        index : Optional[int]
            The page number to get the tutorials from.
        query : Optional[str]
            The string query to look for in the tutorial title, optional.
        difficulty : Optional[Difficulty]
            Enum type representing the difficulty of the tutorial, optional.
        tutorial_type : Optional[TutorialCategory]
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/tutorials/page/{index}", params=params)


class GetWaresMixin:
    """Abstrac class implementing get_software and get_hardware"""

    def get_hardware(
        self,
        index: int = 1,
        *,
        query: str = None,
        status: Status = None,
        category: HardwareCategory = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/hardware/page/{index}", params=params)

    def get_software(
        self,
        index: int = 1,
        *,
        query: str = None,
        status: Status = None,
        category: SoftwareCategory = None,
        timeframe: TimeFrame = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
        """Get a page of software for the platform. Each page will yield up to 30 software.

        Parameters
        -----------
        index : Optional[int]
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
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/software/page/{index}", params=params)


class RSSFeedMixin:
    def rss(self, type: RSSType):
        """Get the RSS feed url for the page depending on which feed type you want

        Parameters
        -----------
        type : RSSType
            The type of feed you desire to get

        Returns
        --------
        str
            URL for the feed type
        """
        return f"https://rss.moddb.com/{self._type.name}/{self.name_id}/{type.name}/feed/rss.xml"


class GetAddonsMixin:
    def get_addons(
        self,
        index: int = 1,
        *,
        query: str = None,
        addon_type: AddonCategory = None,
        timeframe: TimeFrame = None,
        licence: Licence = None,
        sort: Tuple[str, str] = None,
    ) -> ResultList:
        """Get a page of addons for the page. Each page will yield up to 30 addons.

        Parameters
        -----------
        index : Optional[int]
            The page number to get the addons from.
        query : Optional[str]
            The string query to search for in the addon name, optional.
        addon_type : Optional[AddonCategory]
            Type enum defining what category the file is.
        timeframe : Optional[TimeFrame]
            Time frame of when the file was added, optional
        licence : Optional[Licence]
            The licence for the addon, optional
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

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
            "licence": licence.value if licence else None,
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }
        return self._get(f"{self.url}/addons/page/{index}", params=params)


class GetWatchersMixin:
    def get_watchers(self, index: int = 1, *, query: str = None, sort: Tuple[str, str] = None) -> ResultList:
        """Get a page of watchers for the page. Each page will yield up to 30 members.

        Parameters
        -----------
        index : Optional[int]
            The page number to get the watchers from.
        query : Optional[str]
            The string query to search for in the watcher name, optional.
        sort : Optional[Tuple[str, str]]
            The sorting tuple to sort by the results

        Returns
        --------
        ResultList[Thumbnail]
            The list of member type thumbnails parsed from the page
        """

        params = {
            "filter": "t",
            "kw": query,
            "sort": f"{sort[0]}-{sort[1]}" if sort else None,
        }

        return self._get(f"{self.url}/watchers/page/{index}", params=params)
    
class GetTagsMixin:
    def get_tags(self):
        """Get more tags for a page.

        Returns
        --------
        List[Tag]
            List of returned tags
        """

        params = {
            "ajax": "t",
            "sitearea": get_sitearea(self.url),
            "siteareaid": self.id
        }

        resp = get_page(f"{BASE_URL}/tags/ajax/more", params=params, json=True)

        return [Tag(**tag) for tag in resp["tags"].values()]
