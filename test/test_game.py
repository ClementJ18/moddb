import unittest
import moddb

import logging
logger = logging.getLogger('moddb')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class TestGame(unittest.TestCase):
    def test_parse(self):
        self.games = []
        urls = [
            "https://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king",
            "https://www.moddb.com/games/mount-blade-warband",
            "https://www.moddb.com/games/minecraft",
            "https://www.moddb.com/games/half-life-2",
            "https://www.moddb.com/games/tetrifights",
            "https://www.moddb.com/games/malison-the-beginning-of-the-end",
            "https://www.moddb.com/games/chains-of-fate",
            "https://www.moddb.com/games/fatal-offensive-14",
            "https://www.moddb.com/games/krunkerio",
            "https://www.moddb.com/games/polygons-royal"
        ]

        for url in urls:
            soup = moddb.soup(url)
            self.games.append(moddb.Game(soup))

    def test_gets(self):
        teams_users = []
        
        for game in self.games:
            game.get_comments()
            game.get_mods()
            game.get_addons()
            game.get_reviews()
            game.get_articles()
            game.get_files()
            game.get_images()
            game.get_videos()
            game.get_tutorials()