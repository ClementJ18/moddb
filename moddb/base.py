import requests
from .enums import SearchCategory, RSSType
from .boxes import PartialTag, ResultList, Tag, _parse_results
from .utils import (
    get_page,
    get_page_type,
    BASE_URL,
    generate_login_cookies,
    request,
    soup,
)
from .pages import FrontPage, Member

import sys
from typing import Tuple, Any, Union

__all__ = ["search", "parse_page", "login", "logout", "front_page", "parse_results"]


def search(
    category: SearchCategory,
    *,
    query: str = None,
    sort: Tuple[str, str] = None,
    page: int = 1,
    **filters,
) -> ResultList:
    """Search for for a certain type of models and return a list of thumbnails of that
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
    ResultList
        The search object containing the current query settings (so at to be able to redo the search easily),
        pagination metadata and helper methods to navigate the list of results.
    """
    sort_ready = f"{sort[0]}-{sort[1]}" if sort else None

    game = filters.get("game", None)
    game = game.id if game else None

    url = f"{BASE_URL}/{category.name}/page/{page}"
    filter_parsed = {key: value.value for key, value in filters.items() if hasattr(value, "value")}

    params = {
        "filter": "t",
        "kw": query,
        "sort": sort_ready,
        "game": game,
        "year": filters.get("years", None),
        **filter_parsed,
    }

    html = get_page(
        url,
        params=params,
    )

    results, current_page, total_pages, total_results = _parse_results(html)

    return ResultList(
        results=results,
        total_pages=total_pages,
        current_page=current_page,
        params=params,
        url=f"{BASE_URL}/{category.name}",
        total_results=total_results,
    )


def parse_page(url: str) -> Any:
    """Parse a url and return the appropriate object.

    Parameters
    ------------
    url : str
        The url to parse

    Returns
    --------
    Model
        The parsed page as the instance of the model the page represents, can be anything like
        Mod or Game
    """

    html = get_page(url)
    page_type = get_page_type(url)

    model = getattr(sys.modules["moddb"], page_type.name.title())(html)
    return model


def parse_results(url: str, *, params: dict = {}) -> ResultList:
    """Parse a list of results and return them as a
    list of thumbnails.

    Parameters
    -----------
    url : str
        The url of the result list to parse

    Returns
    --------
    ResultList
        The list of thumbnails, wrapped in a ResultList
        so as to benefit from the helper methods that
        help with navigation
    """

    resp = request(requests.Request("GET", url, params=params))
    html = soup(resp.text)

    results, current_page, total_pages, total_results = _parse_results(html)

    parts = resp.url.split("?")
    url = parts[0].split("/page")[0]

    filters = {}
    if len(parts) > 1:
        for filter in parts[1].split("&"):
            key, value = filter.split("=")
            filters[key] = value

    return ResultList(
        results=results,
        total_pages=total_pages,
        current_page=current_page,
        url=url,
        total_results=total_results,
        params=filters,
    )


def login(username: str, password: str) -> Member:
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

    sys.modules["moddb"].SESSION.cookies = generate_login_cookies(username, password)
    return Member(get_page(f"{BASE_URL}/members/{username.replace('_', '-')}"))


def logout():
    """Logs the user out by clearing the cookies, all unapproved guest comments will be hidden and
    all private groups will be hidden once more
    """
    sys.modules["moddb"].SESSION.cookies.clear()


def front_page() -> FrontPage:
    """This returns a model representing the front page of  May sound fancy but it is no more
    than a collection of popular mods, files, games and articles. In addition jobs are listed
    and a poll.

    Returns
    --------
    FrontPage
        The front page object.

    """
    html = get_page(BASE_URL)
    return FrontPage(html)


def rss(rss_type: RSSType):
    """Get the RSS feed url for the entire site depending on which feed type you want

    Parameters
    -----------
    rss_type : RSSType
        The type of feed you desire to get

    Returns
    --------
    str
        URL for the feed type
    """
    return f"https://rss.moddb.com/{rss_type.name}/feed/rss.xml"


def search_tags(tag : Union[str, PartialTag, Tag]):
    """Search for entities tagged with a tag-id or Tag.

    Parameters
    -----------
    tag : Union[str, PartialTag, Tag]
        Either a name-id or the Tag to search for

    Returns
    --------
    ResultList[Thumbnail]
        List of entities tagged with this
    """
    if isinstance(tag, (Tag, PartialTag)):
        tag = tag.name_id

    url = f"https://www.moddb.com/tags/{tag}"
    return parse_results(url)
