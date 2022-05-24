import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb

@patch("moddb.utils.request", new=patched_request)
class TestTeam(unittest.TestCase):
    def setUp(self):
        self.team = moddb.pages.Team(moddb.get_page(getattr(self, "url", "https://www.moddb.com/company/edainmod-dev-team")))

    def test_get_addons(self):
        addons = self.team.get_addons()
        self.team.get_addons(2)
        self.team.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.team.get_articles()
        self.team.get_articles(4)
        self.team.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.team.get_comments()
        self.team.get_comments(4)

    def test_get_engines(self):
        engines = self.team.get_engines()
        self.team.get_engines(3)

        for engine in engines:
            engine.parse()

    def test_get_files(self):
        files = self.team.get_files()
        self.team.get_files(4)
        self.team.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_games(self):
        games = self.team.get_games()
        self.team.get_games(3)

        for game in games:
            game.parse()

    def test_get_hardware(self):
        hardwares = self.team.get_hardware()
        self.team.get_hardware(3)

        for hardware in hardwares:
            hardware.parse()

    def test_get_images(self):
        images = self.team.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_mods(self):
        mods = self.team.get_mods()
        self.team.get_mods(3)

        for mod in mods:
            mod.parse()

    def test_get_software(self):
        softwares = self.team.get_software()
        self.team.get_software(3)

        for software in softwares:
            software.parse() 

    def test_get_tutorials(self):
        tutorials = self.team.get_tutorials()
        self.team.get_tutorials(3)
        self.team.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()   

    def test_get_videos(self):
        videos = self.team.get_videos()

        for video in videos:
            video.parse()
