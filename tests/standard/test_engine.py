import pytest

from tests.utils import sample_list

import moddb

DEFAULT = "https://www.moddb.com/engines/sage-strategy-action-game-engine"

pytestmark = [pytest.mark.vcr]


class EngineBase:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.engine = moddb.Engine(moddb.get_page(request.param))


class TestEnginePatched(EngineBase):
    def test_get_articles(self):
        articles = self.engine.get_articles()
        self.engine.get_articles(4)
        self.engine.get_articles(category=moddb.ArticleCategory.news)

        for article in sample_list(articles, 3):
            article.parse()

    def test_get_comments(self):
        self.engine.get_comments()
        self.engine.get_comments(4)

    def test_get_games(self):
        games = self.engine.get_games()
        self.engine.get_games(3)

        for game in sample_list(games, 3):
            game.parse()

    def test_get_images(self):
        images = self.engine.get_images()

        for image in sample_list(images, 3):
            image.parse()

    def test_get_reviews(self):
        self.engine.get_reviews()
        self.engine.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.engine.get_tutorials()
        self.engine.get_tutorials(3)
        self.engine.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in sample_list(tutorials, 3):
            tutorial.parse()

    def test_get_videos(self):
        videos = self.engine.get_videos()

        for video in sample_list(videos, 3):
            video.parse()

    def test_get_watchers(self):
        self.engine.get_watchers()


class TestEngine(EngineBase):
    def test_get_tags(self):
        tags = self.engine.get_tags()
        # if tags:
        #     random.choice(tags)._get_members()
