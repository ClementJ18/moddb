# -*- coding: utf-8 -*-

class Page():
    """    
    name : str
        Name of the Mod/Game
    desc : str
        Short description of the Mod/Game
    tags : list
        List of :class: `Tag`
    url : str
        URL of the Mod/Game, the one supplied in the :func: parse_mod()
    comment : str
        URL to the comment form for that Mod/Game
    follow : str
        URL to follow the Mod/Game
    suggestions : list
        List of :class: `Suggestion`
    rank : str
        Rank of the Mod/Game
    contact : str
        URL to contact the Development Team for the Mod
    homepage : str
        URL to the homepage supplied by the Development Team for the Mod
    share_link : None
        For future implementation of the share link, None at the moment
    articles : list
        List of :class: `Article`
    count : :class: `Count`
        The :class: `Count` which represent statistics on the Mod/Game
    style : :class: `Style`
        The :class: `Style` which represents the different style information gathered on the Mod/Game
    """
    
    def __init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact, homepage, share_links, articles, count, style):
        self.name = name
        self.desc = desc
        self.tags = tags
        self.url = url
        self.comment = comment
        self.follow = follow
        self.suggestions = suggestions
        self.rank = rank
        self.contact = contact
        self.homepage = homepage
        self.share_links = share_links
        self.articles = articles
        self.count = count
        self.style = style

    def __str__(self):
        return self.name             


class Mod(Page):
    """Mod object for scrapped mod pages, inherits from the :class: `Page` object. Any of these can be 
    None if the data isn't found on the page. Usually happens on smaller mod pages.
    
    **Attributes**
    {}

    game : str
        Name of the game the Mod is created for
    game_url : str
        URL for the game the Mod is created for
    rating : float
        Rating of the mod out of ten
    last_update : str
        Last time the mod showed a sign of life (new video, new file, new article, new image)
    release_date : str
        When the mod was released, will be 'TBD' if it hasn't be released yet
    publishers : str
        Name of the publishers of the Mod
    """
    __doc__ = __doc__.format(Page.__doc__)

    def __init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact, homepage, share_links, articles, count, style, game, game_url, rating, last_update, release_date, publishers):
        Page.__init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact_url, homepage, share_links, articles, count, style)
        self.game = game
        self.game_url = game_url
        self.rating = rating
        self.last_update = last_update
        self.release_date = release_date
        self.publishers = publishers

class Game(Page):
    """Game object for scrapped game pages. Any of the attrbiutes can potentially be None if the 
    data is not foud on the page
    
    **Attributes**
    {}
    
    engine : str
        Name of the Game engine
    engine_url : str
        URL for the Game engine
    publishers : str
        Name of the Game publishers
    rating : float
        Rating of the Game out of ten
    last_update : str
        Last time the Game showed a sign of life (new video, new file, new article, new image)
    boxart : str
        URL to the image for the Game's boxart
    release_date : str
        When the mod was released, will be 'TBD' if it hasn't be released yet
    """

    __doc__ = __doc__.format(Page.__doc__)

    def __init__(self, name, desc, tags, url, comment, follow_url, suggestions, rank, contact, homepage, share_links, articles, count, style, engine, engine_url, rating, players, project, boxart, release_date):
        Page.__init__(self, name, desc, tags, url, comment, follow_url, suggestions, rank, contact_url, homepage, share_links, articles, count, style)
        self.engine = engine
        self.engine_url = engine_url
        self.publishers = publishers
        self.rating = rating
        self.project = project
        self.boxart = boxart
        self.release_date = release_date


class Engine(Page):
    """In progress..."""

    def __init__():
        pass

class Dev(Page):
    """In progress..."""

    def __init__():
        pass

class Group(Page):
    """In progress..."""

    def __init__():
        pass

class Tag():
    """Object for tags scrapped. 

    **Attributes**

    name : str
        Name of the tag
    url : str
        URL of the tag
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url

class Article():
    """Object for scrapped articles from the rss soup object.

    **Attributes**

    title : str
        Title of the article
    desc : str
        The short description of the article
    url : str
        URL to the article
    date : str
        Date the article was published
    """

    def __init__(self, title, desc, url, date):
        self.title = title
        self.desc = desc
        self.url = url
        self.date = date

class Suggestion():
    """Object for scrapped suggestions.

    **Attributes**

    name : str
        Name of the Mod/Game suggested
    url : str
        URL to that Mod/Game
    image : str
        URL to the thumbnail for the Mod/Game
    """

    def __init__(self, name, url, image):
        self.name = name
        self.url = url
        self.image = image

class Count():
    """Object for scrapped statistics. All variable here are number of that variable name (number of articles, number of 
    followers, number of visits, ect...)

    **Attributes**

    visits : str
        Is composed of the total amount of visits over time and the visits today
    followers : int
        Number of users watching this mod/game
    file : int
        Number of files uploaded by this mod/game
    articles : int
        Number of articles published by the mod/game
    reviews : int
        Number of reviews the game/mod has received
    """

    def __init__(self, visits, followers, files, articles, reviews):
        self.visits = visits
        self.followers = followers
        self.files = files
        self.articles = articles
        self.reviews = reviews

class GameCount(Count):
    """mods : int
        Number of mods for the game (exclusive to games)
    """

    __doc__ = Count.__doc__ + __doc__

    def __init__(self, visits, followers, files, articles, reviews, mods):
        Count.__init__(visits, followers, files, articles, reviews)
        self.mods = mods

class Style():
    """Object for scrapped style details from pages.
    
    **Attributes**
    
    genre : str
        The genre of the mod/game (Strategy, Turn based, ect...)
    theme : str
        The theme of the mod/game (fantasy, sci-fi, historical, ect...)
    players : str
        The player style of the mod/game (singeplayer, multiplayer, both, ect...)
    """

    def __init__(self, genre, theme, players):
        self.genre = genre
        self.theme = theme
        self.players = players

