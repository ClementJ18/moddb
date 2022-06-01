import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/engines/sage-strategy-action-game-engine"

@patch("moddb.utils.request", new=patched_request)
class TestEngine:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.engine = moddb.Engine(moddb.get_page(request.param))
    
    def test_get_articles(self):
        articles = self.engine.get_articles()
        self.engine.get_articles(4)
        self.engine.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.engine.get_comments()
        self.engine.get_comments(4)

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

    def test_get_watchers(self):
        self.engine.get_watchers()
