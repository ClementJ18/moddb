import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/mods/edain-mod"

@patch("moddb.utils.request", new=patched_request)
class TestMod:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.mod = moddb.Mod(moddb.get_page(request.param))

    def test_get_addons(self):
        addons = self.mod.get_addons()
        self.mod.get_addons(2)
        self.mod.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.mod.get_articles()
        self.mod.get_articles(4)
        self.mod.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.mod.get_comments()
        self.mod.get_comments(4)

    def test_get_files(self):
        files = self.mod.get_files()
        self.mod.get_files(4)
        self.mod.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_images(self):
        images = self.mod.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_reviews(self):
        self.mod.get_reviews()
        self.mod.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.mod.get_tutorials()
        self.mod.get_tutorials(3)
        self.mod.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.mod.get_videos()

        for video in videos:
            video.parse()

    def test_get_watchers(self):
        self.mod.get_watchers()
