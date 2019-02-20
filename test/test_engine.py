import unittest
import moddb

class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = moddb.pages.Engine(moddb.soup(getattr(self, "url", "https://www.moddb.com/engines/sage-strategy-action-game-engine")))

    def test_get_addons(self):
        addons = self.engine.get_addons()
        self.engine.get_addons(2)
        self.engine.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.engine.get_articles()
        self.engine.get_articles(4)
        self.engine.get_articles(category=moddb.ArticleType.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.engine.get_comments()
        self.engine.get_comments(4)

    def test_get_files(self):
        files = self.engine.get_files()
        self.engine.get_files(4)
        self.engine.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_games(self):
        games = self.engine.get_games()
        self.engine.get_games(3)

        for game in games:
            game.parse()

    def test_get_images(self):
        images = self.engine.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_reviews(self):
        self.engine.get_reviews()
        self.engine.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.engine.get_tutorials()
        self.engine.get_tutorials(3)
        self.engine.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.engine.get_videos()

        for video in videos:
            video.parse()
