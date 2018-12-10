from .enums import SearchCategory, ThumbnailType
from .boxes import Thumbnail
from .utils import soup, LOGGER, normalize

import re
import sys
from typing import List
from robobrowser import RoboBrowser

class Search:
    def __init__(self, **kwargs):
        self.results = kwargs.get("results")
        self.category = kwargs.get("category")
        self.filters = kwargs.get("filters")
        self.page_max = kwargs.get("page_max")
        self.page = kwargs.get("page")
        self.query = kwargs.get("query")
        self.results_max = kwargs.get("results_max")

    def next_page(self):
        if self.page == self.page_max:
            raise ValueError("Reached last page already")

        return search(self.query, self.category, page=self.page+1, **self.filters)

    def previous_page(self):
        if self.page == 1:
            raise ValueError("Reached first page already")

        return search(self.category, query=self.query, page=self.page-1, **self.filters)

    def __repr__(self):
        return f"<Search results={len(self.results)}/{self.results_max}, category={self.category.name} pages={self.page}/{self.page_max}>"

def search(category : SearchCategory, **filters) -> List[Thumbnail]:
    """ Search ModDB.com for a certain type of models and return a list of thumbnails of that 
    model. This function was created to make full use of moddb's filter and sorting system as
    long as the appropriate parameters are passed. Because this function is a single one for every
    model type in moddb the parameters that can be passed vary between model type but the
    documentation will do its best to document all the possibilities. All the objects listed in this
    function are enumerations.

    Sorting
    --------
    You may sort results if you wish before the request is sent, only one sorting argument 
    can be used, the "sort" field takes a tuple which contains the field you wish to sort by
    (described later) and the second element being either "asc" or "desc" based on whether you want
    it sorted in ascendant or descandant order.

    Fields:
        released - when the object was released, asc is oldest, desc is most recent
        id - when it was added to moddb, asc is oldest, desc is most recent
        ranktoday - order by daily ranking, asc is highest ranked, desc is lowest rank
        visitstotal - order by most views, asc is highest views, desc is lowest views
        rating - order by rating, asc is highest rating, desc is lowest rating
        name - order alphabetically, asc is a-z, desc is z-a
        

    Common Parameters
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

    game : object
        An game object or an object with an id attrbiute which represents the
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
    """

    page = filters.pop('page', 1)
    query = filters.pop("query", "")

    sort = filters.pop("sort", None)
    sort = f"{sort[0]}-{'asc' if sort[1] else 'desc'}" if sort else ""

    game = filters.pop("game", None)
    game = game.id if game else ""

    url = f"https://www.moddb.com/{category.name}/page/{page}"
    SESSION = sys.modules["moddb"].SESSION
    filter_parsed = {key : value.value for key, value in filters.items()}
    cat = ThumbnailType[category.name[0:-1]]

    html = soup(url, {"filter": "t", "kw": query, "sort": sort, "game": game, **filter_parsed})

    search_raws = html.find("div", class_="table").find_all("div", recursive=False)[1:]
    pages = len([x for x in html.find("div", class_="pages").children if x != "\n"])
    results = [Thumbnail(url=x.a["href"], name=x.a["title"], type=cat) for x in search_raws]
    results_max = int(normalize(html.find("h5", string=category.name.title()).parent.span.string))

    return Search(results=results, page_max=pages, page=page, filters=filters, 
                  category=category, query=query, results_max=results_max)

def parse(url : str, *, page_type : ThumbnailType = None) -> object:
    regex = r"\/([a-z]+)\/"
    html = soup(url)

    type_mapping = {
        "new": "article"
    }

    if page_type is None:
        page_url = html.find("meta", property="og:url")["content"]
        matches = re.findall(regex, page_url)
        matches.reverse()
        match = matches[0][0:-1] if matches[0].endswith("s") else matches[0]      

        try:
            page_type = ThumbnailType[match]
        except KeyError:
            page_type = ThumbnailType[type_mapping[match]]

        LOGGER.info("%s is type %s", url, page_type)

    model = getattr(sys.modules["moddb"], page_type.name.title())(html)
    return model


def login(username, password):
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

    if not "freeman" in browser.session.cookies:
        raise ValueError(f"Login failed for user {username}")

def logout():
    sys.modules["moddb"].SESSION.cookies.clear()
