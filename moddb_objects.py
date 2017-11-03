class Object():
    """"""
    def __init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact_url, homepage, share_links, articles, count):
        self.name = name
        self.desc = desc
        self.tags = tags
        self.url = url
        self.comment = comment
        self.follow = follow
        self.suggestions = suggestions
        self.rank = rank
        self.contact_url = contact_url
        self.homepage = homepage
        self.share_links = share_links
        self.articles = articles
        self.count = count

    def __str__(self):
        return self.name

class Mod(Object):
    """"""
    def __init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact_url, homepage, share_links, articles, count, game, game_url, rating, genre, theme, players, last_update, release_date, publishers):
        Object.__init__(self, name, desc, tags, url, comment, follow, suggestions, rank, contact_url, homepage, share_links, articles, count)
        self.game = game
        self.game_url = game_url
        self.rating = rating
        self.genre = genre
        self.theme = theme
        self.players = players
        self.last_update = last_update
        self.release_date = release_date
        self.publishers = publishers

class Game(Object):
    """"""
    def __init__(self, name, desc, tags, url, comment, follow_url, suggestions, rank, contact_url, homepage, share_links, articles, count, engine, engine_url, publishers, mods_num, genre, rating, players, project, boxart):
        Object.__init__(self, name, desc, tags, url, comment, follow_url, suggestions, rank, contact_url, homepage, share_links, articles, count)
        self.engine = engine
        self.engine_url = engine_url
        self.publishers = publishers
        self.mods_num = mods_num
        self.genre = genre
        self.rating = rating
        self.players = players
        self.project = project
        self.boxart = boxart


class Engine(Object):
    """"""
    def __init__():
        pass

class Dev(Object):
    """"""
    def __init__():
        pass

class Group(Object):
    """"""
    def __init__():
        pass



class Tag():
    """"""
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Article():
    """"""
    def __init__(self, title, desc, url, date):
        self.title = title
        self.desc = desc
        self.url = url
        self.date = date

class Suggestion():
    """"""
    def __init__(self, name, url, image):
        self.name = name
        self.url = url
        self.image = image

class Count():
    """"""
    def __init__(self, visits, followers, files, articles, reviews):
        self.visits = visits
        self.followers = followers
        self.files = files
        self.articles = articles
        self.reviews = reviews

