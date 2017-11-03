class Mod():
    """"""
    def __init__(self, name, game_name, mod_url, game_url, desc, articles, tags, followers_num, publishers, rating, genre, theme, players, rank, visits_num, files_num, articles_num, reviews_num, last_update, suggestions, homepage, follow_url, comment, release_date):
        self.name = name
        self.game_name = game_name
        self.mod_url = mod_url
        self.game_url = game_url
        self.desc = desc
        self.articles = articles
        self.tags = tags
        self.followers_num = followers_num
        self.publishers = publishers
        self.rating = rating
        self.genre = genre
        self.theme = theme
        self.players = players
        self.rank = rank
        self.visits_num = visits_num
        self.files_num = files_num
        self.articles_num = articles_num
        self.reviews_num = reviews_num
        self.last_update = last_update
        self.suggestions = suggestions
        self.homepage = homepage
        self.follow_url = follow_url
        self.comment = comment
        self.release_date = release_date

class Tag():
    """"""
    def __init__(self, string, url):
        self.string = string
        self.url = url

class Article():
    """"""
    def __init__(self, title, desc, link, date):
        self.title = title
        self.desc = desc
        self.link = link
        self.date = date

class Suggestion():
    """"""
    def __init__(self, string, url, image_url):
        self.string = string
        self.url = url
        self.image_url = image_url


