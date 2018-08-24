import enum

def search(self, url, *, type):
    pass

def soup_page(self, url):
    pass

class BaseFunctions:
    def __init__(self, **attrs):
        self.url = attrs.pop("url")

    def get_comments(self, index : int):
        pass

    def get_all_comments(self):
        pass

    def get_all_articles(self):
        pass

    def get_article(self):
        pass

    def get_file(self):
        pass

    def get_files(self):
        pass

    def get_reviews(self, rating : int):
        pass

    def get_videos(self):
        pass

    def get_images(self):
        pass


class Page(BaseFunctions):
    def __init__(self, **attrs):
        super().__init__(**attrs):
        #Basic Info
        self.name = attrs.pop("name")
        self.description = attrs.pop("description")

        #Interaction Links
        self.comment = attrs.pop("comment")
        self.follow = attrs.pop("follow")
        self.contact = attrs.pop("contact")
        self.share_links = attrs.pop("share_links")
        
        #Advanced Data
        self.rank = attrs.pop("rank")
        self.homepage = attrs.pop("homepage")
        self.rating = attrs.pop("rating")
        self.last_update = attrs.pop("last_update")
        self.release_date = attrs.pop("release_date")
        self.icon = attrs.pop("icon")

        #List of Objects
        self.count = attrs.pop("count")
        self.style = attrs.pop("style")
        self.tags = attrs.pop("tags")
        self.suggestions = attrs.pop("suggestions")
        self.articles = attrs.pop("articles")

        #New Stuff
        self.article = attrs.pop("article")

        #Links for object retrivals
        self._team_url = attrs.pop("team")

    def get_team(self):
        pass

class Mod(Page):
    def __init__(self, **attrs):
        #Inheritance
        super().__init__(**attrs)
        
        #Mod Specific Data
        self.game = attrs.pop("game")
        self.game_url = attrs.pop("game_url")

    def get_game(self):
        pass

class Game(Page):
    def __init__(self, **attrs):
        #Inheritance
        super().__init__(**attrs)
        
        #Game Specific Data
        self.engine = attrs.pop("engine")
        self.engine_url = attrs.pop("engine_url")
        self.project = attrs.pop("project")
        self.boxart = attrs.pop("boxart")

    def get_engine(self):
        pass

class Article:
    def __init__(self, **attrs):
        self.title = attrs.pop("title")
        self.desc = attrs.pop("desc")
        self.url = attrs.pop("url")
        self.date = attrs.pop("date")        

        #new stuff
        self.suggestions = attrs.pop("suggestions")
        self.html = attrs.pop("html")

    def to_text(self):
        pass

class ThumbnailType(enum.Enum):
    mod = 0
    game = 1
    engine = 2
    user = 3
    group = 4
    article = 5
    review = 6

class ThumbnailObject:
    def __init__(self, **attrs):
        self.name = attrs.pop("name")
        self.url = attrs.pop("url")
        self.image = attrs.pop("image")
        self.summary = attrs.pop("summary")
        self.type = attrs.pop("type")

    def get_object(self):
        pass

class Count:
    def __init__(self, **attrs):
        self.visits = attrs.pop("visits")
        self.followers = attrs.pop("followers")
        self.files = attrs.pop("files")
        self.articles = attrs.pop("articles")
        self.reviews = attrs.pop("reviews")

class GameCount(Count):
    def __init__(self, **attrs):
        super().__init__(**attrs)
        self.mods = attrs.pop("mods")

class Style:
    def __init__(self, **attrs):
        self.genre = attrs.pop("genre")
        self.theme = attrs.pop("theme")
        self.players = attrs.pop("players")

class Tag:
    def __init__(self, **attrs):
        self.name = attrs.pop("name")
        self.url = attrs.pop("url")

class Share:
    def __init__(self, **attrs):
        self.facebook = attrs.pop("facebook")
        self.twitter = attrs.pop("twitter")
        self.email = attrs.pop("email")
        self.reddit = attrs.pop("reddit")

class Comment:
    def __init__(self, **attrs):    
        self.date = attrs.pop("date")
        self.position = attrs.pop("position")
        self.karma = attrs.pop("karma")
        self.content = attrs.pop("content")
        self.positive_karma = attrs.pop("positive_karma")
        self.negative_karma = attrs.pop("negative_karma")
        self.reply = attrs.pop("reply")

        self._author_url = attrs.pop("author_url")

    def get_author(self):
        pass


class User(BaseFunctions):
    def __init__(self, **attr):
        super().__init__(**attrs)

        self.name = attrs.pop("name")
        self.url = attrs.pop("url")
        self.summary = attrs.pop("summary")

        self.level = attrs.pop("level")
        self.avatar = attrs.pop("avatar")
        self.status = attrs.pop("status")
        self.country = attrs.pop("country")
        self.gender = attrs.pop("gender")
        self.friend = attrs.pop("friend")
        self.follow = attrs.pop("follow")
        self.blogs = attrs.pop("blogs")

class Blogs:
    def __init__(self, **attrs):
        self.url = attrs.pop("url")
        self.name = attrs.pop("name")
        self._author_url = attrs.pop("author_url")
        self.date = attrs.pop("date")
        self.html = attrs.pop("html")

    def to_text(self):
        pass

    def get_author(self):
        pass

