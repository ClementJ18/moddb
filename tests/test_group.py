import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/groups/humour-satire-parody"

@patch("moddb.utils.request", new=patched_request)
class TestGroup:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.group = moddb.Group(moddb.get_page(request.param))

    def test_get_addons(self):
        addons = self.group.get_addons()
        self.group.get_addons(2)
        self.group.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()

    def test_get_articles(self):
        articles = self.group.get_articles()
        self.group.get_articles(4)
        self.group.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.group.get_comments()
        self.group.get_comments(4)

    def test_get_files(self):
        files = self.group.get_files()
        self.group.get_files(4)
        self.group.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_images(self):
        images = self.group.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_tutorials(self):
        tutorials = self.group.get_tutorials()
        self.group.get_tutorials(3)
        self.group.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.group.get_videos()

        for video in videos:
            video.parse()

    def test_get_watchers(self):
        self.group.get_watchers()
