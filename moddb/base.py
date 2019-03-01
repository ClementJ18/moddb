from .enums import SearchCategory, ThumbnailType
from .boxes import Thumbnail
from .utils import get_page, LOGGER, normalize, get_type_from
from .pages import FrontPage, Member

import re
import sys
from typing import Tuple, Any
from robobrowser import RoboBrowser

__all__ = ["Search", "search", "parse", "login", "logout", "front_page"]

class Search:
    """Represents the search you just conducted through the library's search function. Can be used to navigate 
    the search page efficiently.

    Attributes
    -----------
    results : List[Thumbnail]
        The list of results the search returned
    category : ThumbnailType
        The type results
    filters : dict{str : Enum}
        The dict of filters that was used to search for the results
    page_max : int
        The number of pages
    page : int
        The current page, range is 1-page_max included
    query : str
        The text query that was used in the search
    results_max : int
        The total number of results for this search
    filters : dict
        Dictionnary of filters used to keep the query list persistent, can also be
        unpacked and passed to the search function.

    """
    def __init__(self, **kwargs):
        self.results = kwargs.get("results")
        self.category = kwargs.get("category")
        self.filters = kwargs.get("filters")
        self.page_max = kwargs.get("page_max")
        self.page = kwargs.get("page")
        self.query = kwargs.get("query")
        self.results_max = kwargs.get("results_max")
        self.sort = kwargs.get("sort")

    def next_page(self) -> 'Search':
        """Returns a new search object with the next page of results, will raise ValueError 
        if the last page is the current one

        Returns
        --------
        Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no next page
        """
        if self.page == self.page_max:
            raise ValueError("Reached last page already")

        return self.to_page(self.page+1)

    def previous_page(self) -> 'Search': 
        """Returns a new search object with the previous page of results, will raise 
        ValueError if the first page is the current one

        Returns
        --------
        Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            There is no previous page
        """
        if self.page == 1:
            raise ValueError("Reached first page already")

        return self.to_page(self.page-1)

    def to_page(self, page : int) -> 'Search': 
        """Returns a new search object with results to a specific page in the search results 
        allowing for fast navigation. Will raise ValueError if you attempt to navigate out 
        of bounds.
    
        Parameters
        -----------
        page : int
            A page number within the range 1 - page_max inclusive

        Returns
        --------
        Search
            The new search objects containing a new set of results.

        Raises
        -------
        ValueError
            This page does not exist
        """
        if page < 1 or page > self.page_max:
            raise ValueError(f"Please pick a page between 1 and {self.page_max}")

        return search(self.category, query=self.query, page=page, sort=self.sort, **self.filters)

    def resort(self, new_sort : Tuple[str, str]) -> 'Search': 
        """Allows you to sort the whole search by a new sorting parameters. Returns a new search object.

        Parameters
        -----------
        new_sort : Tuple[str, str]
            The new sorting tuple to check by

        Returns
        -------
        Search
            The new set of results with the updated sort order
        """
        return search(self.category, query=self.query, page=1, sort=new_sort, **self.filters)

    def __repr__(self):
        return f"<Search results={len(self.results)}/{self.results_max}, category={self.category.name} pages={self.page}/{self.page_max}>"

    def __iter__(self):
        return self.results.__iter__()

    def __getitem__(self, key):
        return self.results[key]

def search(category : SearchCategory, *, query : str = None, sort : Tuple[str, str] = None,
           page : int = 1, **filters) -> Search: 
    """ Search for for a certain type of models and return a list of thumbnails of that 
    model. This function was created to make full use of moddb's filter and sorting system as
    long as the appropriate parameters are passed. Because this function is a single one for every
    model type in moddb the parameters that can be passed vary between model type but the
    documentation will do its best to document all the possibilities. All the objects listed in this
    function are enumerations. Finally it is key to note that the result attribute of the returned search
    object is not a list of the parsed pages but a list of Thumbnail objects containing the image, url,
    name and type of the object on which. Call the thumbnail's parse method and it will return the full model.

    Parameters
    ------------
    category : SearchCategory
        The model type that you want to search

    query : str
        String to search for in the model title
    
    sort : Tuple[str, str]
        The tuple to sort by, look at the models your are searching for documentation 
        on sorting.

    page : int
        The page of results to get first

    filters : dict
        Search filters

    Returns
    --------
    Search
        The search object containing the current query settings (so at to be able to redo the search easily),
        pagination metadata and helper methods to navigate the list of results.
    """
    sort_ready = f"{sort[0]}-{sort[1]}" if sort else None

    game = filters.get("game", None)
    game = game.id if game else None

    url = f"https://www.moddb.com/{category.name}/page/{page}"
    filter_parsed = {key : value.value for key, value in filters.items() if hasattr(value, "value")}
    cat = ThumbnailType[category.name[0:-1]]

    html = get_page(url, params={"filter": "t", "kw": query, "sort": sort_ready, "game": game, **filter_parsed})

    search_raws = html.find("div", class_="table").find_all("div", recursive=False)[1:]
    
    try:
        pages = int(html.find("div", class_="pages").find_all()[-1].string)
    except AttributeError:
        LOGGER.info("Search query %s has less than 30 results (only one page)", url)
        pages = 1

    results = [Thumbnail(url=x.a["href"], name=x.a["title"], type=cat, image=x.a.img["src"]) for x in search_raws]
    results_max = int(normalize(html.find("h5", string=category.name.title()).parent.span.string))
    return Search(results=results, page_max=pages, page=page, filters=filters, 
                  category=category, query=query, results_max=results_max, sort=sort)

def parse(url : str, *, page_type : ThumbnailType = None) -> Any: 
    """Parse a url and return the appropriate object. The function will attempt to figure out the page itself
    from the url and the content of the page but ModDB is not always consistent with this. In which case
    it is recommended to pass a Thumbnail enum to the `page_type` kwarg.

    Parameters
    ------------
    url : str
        The url to parse

    page_type : Optional[ThumbnailType]
        The type of the page you are parsing, used to decide which model to parse the html with
        can be left blank to let the function take care of it but might not always lead to the
        correct result.

    Returns
    --------
    Model
        The parsed page as the instance of the model the page represents, can be anything like
        Mod or Game
    """

    html = get_page(url)
    page_type = get_type_from(url)

    model = getattr(sys.modules["moddb"], page_type.name.title())(html)
    return model


def login(username : str, password : str) -> Member: 
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

    Returns
    --------
    Member
        The member you are logged in as
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

    return Member(get_page(f"https://www.moddb.com/members/{username}"))

def logout(): 
    """Logs the user out by clearing the cookies, all unapproved guest commnets will be hidden and 
    all private groups will be hidden once more
    """
    sys.modules["moddb"].SESSION.cookies.clear()

def front_page() -> FrontPage:
    """This returns a model representing the front page of  May sound fancy but it is no more
    than a collection of popular mods, files, games and articles. In addition jobs are listed (but
    not linked so unparsable) and a poll.

    Returns
    --------
    FrontPage
        The front page object.
        
    """
    html = get_page("https://www.moddb.com")
    return FrontPage(html)
