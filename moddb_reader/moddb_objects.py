class Page():
    def __init__(self, name, desc, url, comment, follow, contact, share_links, rank, homepage, rating, last_update, release_date, publishers, icon, count, style, tags, suggestions, articles):
        #Basic Info
        self.name = name
        self.desc = desc
        self.url = url

        #Interaction Links
        self.comment = comment
        self.follow = follow
        self.contact = contact
        self.share_links = share_links
        
        #Advanced Data
        self.rank = rank
        self.homepage = homepage
        self.rating = rating
        self.last_update = last_update
        self.release_date = release_date
        self.publishers = publishers
        self.icon = icon

        #List of Objects
        self.count = count
        self.style = style
        self.tags = tags
        self.suggestions = suggestions
        self.articles = articles
        

    def __str__(self):
        return self.name

class Mod(Page):
    def __init__(self, url, desc, publishers, rating, rank, release_date, contact, homepage, last_update, comment, articles, tags, style, suggestions, icon, game, game_url, name, count, follow, share_links):
        #Inheritance
        Page.__init__(self, name, desc, url, comment, follow, contact, share_links, rank, homepage, rating, last_update, release_date, publishers, icon, count, style, tags, suggestions, articles)
        
        #Mod Specific Data
        self.game = game
        self.game_url = game_url

class Game(Page):
    def __init__(self, url, desc, publishers, rating, rank, release_date, contact, homepage, last_update, comment, articles, tags, style, suggestions, icon, engine, engine_url, name, project, boxart, count, follow, share_links):
        #Inheritance
        Page.__init__(self, name, desc, url, comment, follow, contact, share_links, rank, homepage, rating, last_update, release_date, publishers, icon, count, style, tags, suggestions, articles)
        
        #Game Specific Data
        self.engine = engine
        self.engine_url = engine_url
        self.project = project
        self.boxart = boxart

class Article():
    def __init__(self, title, desc, url, date):
        self.title = title
        self.desc = desc
        self.url = url
        self.date = date

class Suggestion():
    def __init__(self, name, url, image):
        self.name = name
        self.url = url
        self.image = image

class Count():
    def __init__(self, visits, followers, files, articles, reviews):
        self.visits = visits
        self.followers = followers
        self.files = files
        self.articles = articles
        self.reviews = reviews

class GameCount(Count):
    def __init__(self, visits, followers, files, articles, reviews, mods):
        Count.__init__(self, visits, followers, files, articles, reviews)
        self.mods = mods

class Style():
    def __init__(self, genre, theme, players):
        self.genre = genre
        self.theme = theme
        self.players = players

class Tag():
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Share():
    def __init__(self, facebook, twitter, email, reddit):
        self.facebook = facebook
        self.twitter = twitter
        self.email = email
        self.reddit = reddit
