import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king"

@patch("moddb.utils.request", new=patched_request)
class TestGame:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_mod(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.game = moddb.Game(moddb.get_page(request.param))

    def test_get_addons(self):
        addons = self.game.get_addons()
        self.game.get_addons(2)
        self.game.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.game.get_articles()
        self.game.get_articles(4)
        self.game.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.game.get_comments()
        self.game.get_comments(4)

    def test_get_files(self):
        files = self.game.get_files()
        self.game.get_files(4)
        self.game.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_images(self):
        images = self.game.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_mods(self):
        mods = self.game.get_mods()
        self.game.get_mods(3)

        for mod in mods:
            mod.parse()

    def test_get_reviews(self):
        self.game.get_reviews()
        self.game.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.game.get_tutorials()
        self.game.get_tutorials(3)
        self.game.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.game.get_videos()

        for video in videos:
            video.parse()

    def test_get_watchers(self):
        self.game.get_watchers()
