#!/usr/bin/python3.6
from moddb_objects import *
from bs4 import BeautifulSoup
import requests

def _url_checker(url, word):
    return url.startswith("http://www.moddb.com/{}/".format(word))

def _soup_page(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")

    resp = requests.get(url.replace("www","rss") + "/articles/feed/rss.xml")
    rss = BeautifulSoup(resp.text, "xml")

    return soup, rss

def _article_parser(rss):
    articles = list()
    article_list = rss.find_all("item")
    for article in article_list:
        title = article.title.string
        desc = article.find_all(type="plain")[1].string
        link = article.link.string
        date = article.pubDate.string[:-14]
        articles.append(Article(title, desc, link, date))
    
    return articles

def _tag_parser(raw_tags, url):
    tags = list()
    for tag in raw_tags:
        name = tag.a.string
        link = url + tag.a["href"]
        tags.append(Tag(name, link))

    return tags

def _mod_page_parser(url, soup, rss):

    def _string_grab(string):
        try:
            return [x.parent.a.string for x in misc if x.string == string][0]
        except IndexError:
            return None

    misc = soup.find_all("h5")
    game = [x.parent.a for x in misc if x.string == "Game"][0]
    game_name = game.string
    game_url = "http://www.moddb.com" + game["href"]

    mod_name = soup.title.string[:-9].replace("for " + game_name, "")
    desc = soup.find("meta", {"name":"description"})["content"]
    
    articles = _article_parser(rss)
    tags = _tag_parser(soup.find(id="tagsform").find_all(class_="row"), url)

    try: 
        publishers = [x.parent.a.string for x in misc if x.string in ["Developer", "Creator"]][0]
    except IndexError:
        publishers = None

    try:
        rating = float(soup.find(itemprop="ratingValue")["content"])
    except TypeError:
        rating = None

    release_date = soup.time.string

    theme = _string_grab("Theme")
    genre = _string_grab("Genre")
    players = _string_grab("Players")
    rank = _string_grab("Rank")
    visits_total_num = _string_grab("Visits")
    files_num = int(_string_grab("Files"))
    articles_num = int(_string_grab("Articles"))
    reviews_num = int(_string_grab("Reviews"))
    followers_num = int(_string_grab("Watchers"))

    try:
        contact_url = url + [x.parent.a["href"] for x in misc if x.string == "Contact"][0]
    except IndexError:
        contact_url = None

    try:
        homepage = [x.parent.a["href"] for x in misc if x.string == "Homepage"][0]
    except IndexError:
        homepage = None

    try:
        last_update = [x.parent.time.string for x in misc if x.string == "Last Update"][0]
    except IndexError:
        last_update = None

    suggestions = list()
    suggestions_raw = soup.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
    for x in suggestions_raw:
        link = x.find("a",class_="heading")
        image_url = link.parent.parent.find("img")["src"]
        suggestion = Suggestion(link.string, url + link["href"], image_url)
        suggestions.append(suggestion)

    try:
        follow_url = url + [x.parent.a["href"] for x in misc if x.string == "Mod watch"][0]
    except IndexError:
        follow_url = None

    comment = url + "#commentform"
    count = Count(visits_total_num, followers_num, files_num, articles_num, reviews_num)
    style = Style(genre, theme, players)

    return Mod(mod_name, desc, tags, url, comment, follow_url, suggestions, rank, contact_url, homepage, None, articles, count, style, game_name, game_url, rating, last_update, release_date, publishers)

def parse_mod(url):
    if _url_checker(url, "mods"):
        soup, rss = _soup_page(url)
        mod = _mod_page_parser(url, soup, rss)
        return mod
    
def _game_page_parser(url, soup, rss):
    
    def _string_grab(string):
        try:
            return [x.parent.a.string for x in misc if x.string == string][0]
        except IndexError:
            return None

    misc = soup.find_all("h5")
    engine = [x.parent.a for x in misc if x.string == "Engine"][0]
    engine_name = engine.string
    engine_url = "http://www.moddb.com" + engine["href"]

    game_name = soup.title.string[:-9].replace(" Windows game", "")
    desc = soup.find("meta", {"name":"description"})["content"]
    
    articles = _article_parser(rss)
    tags = _tag_parser(soup.find(id="tagsform").find_all(class_="row"), url)

    try: 
        publishers = [x.parent.a.string for x in misc if x.string in ["Developer & Publisher", "Developer", "Creator"]][0]
    except IndexError:
        publishers = None

    try:
        rating = float(soup.find(itemprop="ratingValue")["content"])
    except TypeError:
        rating = None

    release_date = soup.time.string

    theme = _string_grab("Theme")
    genre = _string_grab("Genre")
    players = _string_grab("Players")
    rank = _string_grab("Rank")
    visits_num = _string_grab("Visits")
    files_num = int(_string_grab("Files"))
    articles_num = int(_string_grab("Articles"))
    reviews_num = int(_string_grab("Reviews"))
    followers_num = int(_string_grab("Watchers"))
    mods_num = int(_string_grab("Mods"))
    project = _string_grab("Project")
    release_date = _string_grab("Release date")

    try:
        contact_url = url + [x.parent.a["href"] for x in misc if x.string == "Contact"][0]
    except IndexError:
        contact_url = None

    try:
        homepage = [x.parent.a["href"] for x in misc if x.string == "Homepage"][0]
    except IndexError:
        homepage = None

    try:
        last_update = [x.parent.time.string for x in misc if x.string == "Last Update"][0]
    except IndexError:
        last_update = None

    try:
        boxart_url = [x.parent.a["href"] for x in misc if x.string == "Boxart"][0]
    except IndexError:
        boxart_url = None

    suggestions = list()
    suggestions_raw = soup.find(string="You may also like").parent.parent.parent.parent.find_all(class_="row clear")
    for x in suggestions_raw:
        link = x.find("a",class_="heading")
        image_url = link.parent.parent.find("img")["src"]
        suggestion = Suggestion(link.string, url + link["href"], image_url)
        suggestions.append(suggestion)

    try:
        follow_url = url + [x.parent.a["href"] for x in misc if x.string == "Game watch"][0]
    except IndexError:
        follow_url = None

    comment = url + "#commentform"
    count = GameCount(visits_num, followers_num, files_num, articles_num, reviews_num, mods_num)
    style = Style(genre, theme, players)

    return Game(game_name, desc, tags, url, comment, follow_url, suggestions, rank, contact_url, homepage, None, articles, count, engine_name, engine_url, publishers, rating, project, boxart_url)


def parse_game(url):
    if _url_checker(url, "games"):
        soup, rss = _soup_page(url)
        game = _game_page_parser(url, soup, rss)
        return game
