from .enums import SearchCategory, ThumbnailType, Sort
from .boxes import Thumbnail
from .utils import soup, LOGGER, normalize
from .pages import FrontPage

import re
import sys
from typing import Tuple
from robobrowser import RoboBrowser

__all__ = ["Search", "search", "parse", "login", "logout", "front_page"]

class Search:
    """Represents the search you just conducted through the library's search function. Can be used to navigate 
    the search page efficiently.

    Attributes
    -----------
    results : list[moddb.Thumbnail]
        The list of results the search returned

    category : moddb.ThumbnailType
        The type results

    filters : dict{str : moddb.Enum}
        The dict of filters that was used to search for the results

    page_max : int
        The number of pages

    page : int
        The current page, range is 1-page_max included

    query : str
        The text query that was used in the search

    results_max : int
        The total number of results for this search

    """
    def __init__(self, **kwargs):
        self.results = kwargs.get("results")
        self.category = kwargs.get("category")
        self.filters = kwargs.get("filters")
        self.page_max = kwargs.get("page_max")
        self.page = kwargs.get("page")
        self.query = kwargs.get("query")
        self.results_max = kwargs.get("results_max")

    def next_page(self) -> 'Search':
        """Returns a new search object with the next page of results, will raise ValueError 
        if the last page is the current one

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no next page
        """
        if self.page == self.page_max:
            raise ValueError("Reached last page already")

        self.to_page(self.page+1)

    def previous_page(self) -> 'Search': 
        """Returns a new search object with the previous page of results, will raise 
        ValueError if the first page is the current one

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no previous page
        """
        if self.page == 1:
            raise ValueError("Reached first page already")

        return self.to_page(self.page-1)

    def to_page(self, page : range(0, 4)) -> 'Search': 
        """Returns a new search object with results to a specific page in the search results 
        allowing for fast navigation. Will raise ValueError if you attempt to navigate out 
        of bounds.
    
        Parameters
        -----------
        page : int
            A page number within the range 1 - page_max inclusive

        Returns
        --------
        moddb.Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            This page does not exist
        """
        if page < 1 or page > self.page_max:
            raise ValueError(f"Please pick a page between 1 and {self.page_max}")

        return search(self.category, query=self.query, page=page, **self.filters)

    def resort(self, new_sort : Tuple[Sort, str]) -> 'Search': 
        """Allows you to sort the whole search by a new sorting parameters. Returns a new search object.

        Parameters
        -----------
        new_sort : tuple[moddb.Sort, str]
            The new sorting tuple to check by

        Return
        -------
        moddb.Search
            The new set of results with the updated sort order
        """
        return search(self.category, query=self.query, page=1, sort=new_sort, **self.filters)

    def __repr__(self):
        return f"<Search results={len(self.results)}/{self.results_max}, category={self.category.name} pages={self.page}/{self.page_max}>"


def search(category : SearchCategory, **filters) -> Search: 
    """ Search ModDB.com for a certain type of models and return a list of thumbnails of that 
    model. This function was created to make full use of moddb's filter and sorting system as
    long as the appropriate parameters are passed. Because this function is a single one for every
    model type in moddb the parameters that can be passed vary between model type but the
    documentation will do its best to document all the possibilities. All the objects listed in this
    function are enumerations. Finally it is key to note that the result attribute of the returned search
    object is not a list of the parsed pages but a list of Thumbnail objects containing the image, url,
    name and type of the object on which. Call the thumbnail's parse method and it will return the full model.

    Return
    -------
    moddb.Search
        The search object containing the current query settings (so at to be able to redo the search easily),
        pagination metadata and helper methods to navigate the list of results.

    Sorting
    --------
    You may sort results if you wish before the request is sent, only one sorting argument 
    can be used, the "sort" field takes a tuple which contains the field you wish to sort by
    (described later) and the second element being either "asc" or "desc" based on whether you want
    it sorted in ascendant or descandant order.

    Fields of moddb.Sort:
        released - when the object was released, asc is oldest, desc is most recent
        id - when it was added to moddb, asc is oldest, desc is most recent
        ranktoday - order by daily ranking, asc is highest ranked, desc is lowest rank
        visitstotal - order by most views, asc is highest views, desc is lowest views
        rating - order by rating, asc is highest rating, desc is lowest rating
        name - order alphabetically, asc is a-z, desc is z-a
        

    Parameters
    ------------------
    category : moddb.SearchCategory
        The model type that you want to search

    query : str
        String to search for in the model title

    Searching for a Mod
    --------------------
    released : moddb.Status
        The status of the mod (released, unreleased)

    genre : moddb.Genre
        The genre of the mod (fps, tower defense)

    theme : moddb.Theme
        The theme of the mod (fantasy, action)

    players : moddb.PlayerStyle
        Player styles of the mod (co-op, singleplayer)

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    game : Union[moddb.Game, moddb.Object]
        An game object or an object with an id attribute which represents the
        game the mod belongs to.

    Searching for a Game
    ---------------------
    released : moddb.Status
        The status of the game (released, unreleased)

    genre : moddb.Genre
        The genre of the game (fps, tower defense)

    theme : moddb.Theme
        The theme of the game (fantasy, action)

    indie : moddb.Scope
        Whether the game is triple AAA or indie

    players : moddb.PlayerStyle
        Player styles of the game (co-op, singleplayer)

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)
    
    Searching for an Engine
    ------------------------
    released : moddb.Status
        The status of the engine (released, unreleased)

    licence : moddb.Licence
        The license of the engine

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    Searching for an Addon
    -----------------------
    category : moddb.AddonCategory
        The type of addon (map, textures, ect...)

    licence : moddb.Licence
        The licence of the addon 

    game : Union[moddb.Game, moddb.Object]
        An game object or an object with an id attribute which represents the
        game the addon belongs to.

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    Searching for a File
    ---------------------
    category  : moddb.FileCategory
        The type of file (audio, video, demo, full version....)

    categoryaddon : moddb.AddonCategory
        The type of addon (map, textures, ect...)

    game : Union[moddb.Game, moddb.Object]
        An game object or an object with an id attribute which represents the
        game the addon belongs to.

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    Searching for an Article
    -------------------------
    type : moddb.ArticleType
        Type of the article (news, feature)

    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    game : Union[moddb.Game, moddb.Object]
        An game object or an object with an id attribute which represents the
        game the addon belongs to.

    Searching for a Review
    -----------------------
    rating : int
        A value from 1 to 10 denoting the rating number you're looking for

    sitearea : moddb.Category
        The type of model the rating is for (mod, engine, game)

    Searching for a Headline
    -------------------------
    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    Searching for a Blog
    ---------------------
    timeframe : moddb.TimeFrame
        The time period this was released in (last 24hr, last week, last month)

    Searching for an Audio, a Video or an Image
    --------------------------------------------
    sitearea : moddb.Category
        The type of model the media belongs to. moddb.Category.downloads is not valid for this.

    Searching for a Team
    ---------------------
    subscriptions : moddb.Membership
        The subscription system of the company (private, invitation)

    category : moddb.TeamCategory
        What does the team do (publisher, developer)

    Searching for a Group
    ----------------------
    subscriptions : moddb.Membership
        The subscription system of the group (private, invitation)

    category : moddb.GroupCategory
        The category of the group (funny, literature)
    """

    page = filters.pop('page', 1)
    query = filters.pop("query", None)

    sort = filters.pop("sort", None)
    sort = f"{sort[0].name}-{sort[1]}" if sort else None

    game = filters.pop("game", None)
    game = game.id if game else None

    url = f"https://www.moddb.com/{category.name}/page/{page}"
    filter_parsed = {key : value.value for key, value in filters.items()}
    cat = ThumbnailType[category.name[0:-1]]

    html = soup(url, params={"filter": "t", "kw": query, "sort": sort, "game": game, **filter_parsed})

    search_raws = html.find("div", class_="table").find_all("div", recursive=False)[1:]
    pages = len([x for x in html.find("div", class_="pages").children if x != "\n"])
    results = [Thumbnail(url=x.a["href"], name=x.a["title"], type=cat, image=x.a.img["src"]) for x in search_raws]
    results_max = int(normalize(html.find("h5", string=category.name.title()).parent.span.string))

    return Search(results=results, page_max=pages, page=page, filters=filters, 
                  category=category, query=query, results_max=results_max)

def parse(url : str, *, page_type : ThumbnailType = None) -> "PageModel": 
    """Parse a url and return the appropriate object. The function will attempt to figure out the page itself
    from the url and the content of the page but ModDB is not always consistent with this. In which case
    it is recommended to pass a moddb.Thumbnail enum to the `page_type` kwarg.

    Parameters
    ------------
    url : str
        The url to parse

    page_type : Optional[moddb.ThumbnailType]
        The type of the page you are parsing, used to decide which model to parse the html with
        can be left blank to let the function take care of it but might not always lead to the
        correct result.

    Returns
    --------
    moddb.Model
        The parsed page as the instance of the model the page represents, can be anything like
        moddb.Mod or moddb.Game
    """

    regex = r"\/([a-z]+)\/"
    html = soup(url)

    type_mapping = {
        "new": "article"
    }

    if page_type is None:
        matches = re.findall(regex, url)
        matches.reverse()
        match = matches[0][0:-1] if matches[0].endswith("s") else matches[0]      

        try:
            page_type = ThumbnailType[match]
        except KeyError:
            page_type = ThumbnailType[type_mapping[match]]

        LOGGER.info("%s is type %s", url, page_type)

    model = getattr(sys.modules["moddb"], page_type.name.title())(html)
    return model


def login(username : str, password : str) -> None: 
    """Login the user to moddb through the library, this allows user to see guest comments and see
    private groups they are part of.

    Parameters
    -----------
    username : str
        The username of the user

    password : str
        The password associated to that username

    Raises
    -------
    ValueError
        The password or username was incorrect
    """

    browser = RoboBrowser(history=True, parser='html.parser')
    browser.open('https://www.moddb.com/members/login')
    t = browser.find_all("form")[1].find_all("input", class_="text", type="text")
    t.remove(browser.find("input", id="membersusername"))
    form = browser.get_form(attrs={"name": "membersform"})

    form["password"].value = password
    form["referer"].value = ""
    form[browser.find("input", id="membersusername")["name"]].value = username
    form[t[0]["name"]].value = ""

    browser.submit_form(form)
    sys.modules["moddb"].SESSION = browser.session

    if "freeman" not in browser.session.cookies:
        raise ValueError(f"Login failed for user {username}")

def logout() -> None: 
    """Logs the user out by clearing the cookies, all guest commnets will be hidden and all private groups
    will be hidden once more
    """
    sys.modules["moddb"].SESSION.cookies.clear()

def front_page() -> FrontPage:
    """This returns a model representing the front page of moddb. May sound fancy but it is no more
    than a collection of popular mods, files, games and articles. In addition jobs are listed (but
    not linked so unparsable) and a poll.

    Returns
    moddb.FrontPage
        The front page object.
    """
    html = soup("https://www.moddb.com/")
    return FrontPage(html)
