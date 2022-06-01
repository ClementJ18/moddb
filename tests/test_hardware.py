import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/hardware/htc-vive"

@patch("moddb.utils.request", new=patched_request)
class TestHardware:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.hardware = moddb.Hardware(moddb.get_page(request.param))

    def test_get_articles(self):
        articles = self.hardware.get_articles()
        self.hardware.get_articles(4)
        self.hardware.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.hardware.get_comments()
        self.hardware.get_comments(4)

    def test_get_files(self):
        files = self.hardware.get_files()
        self.hardware.get_files(4)
        self.hardware.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_games(self):
        games = self.hardware.get_games()
        self.hardware.get_games(3)

        for game in games:
            game.parse()

    def test_get_hardware(self):
        hardwares = self.hardware.get_hardware()
        self.hardware.get_hardware(3)

        for hardware in hardwares:
            hardware.parse()

    def test_get_images(self):
        images = self.hardware.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_reviews(self):
        self.hardware.get_reviews()
        self.hardware.get_reviews(3)

    def test_get_software(self):
        softwares = self.hardware.get_software()
        self.hardware.get_software(3)

        for software in softwares:
            software.parse()  

    def test_get_tutorials(self):
        tutorials = self.hardware.get_tutorials()
        self.hardware.get_tutorials(3)
        self.hardware.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.hardware.get_videos()

        for video in videos:
            video.parse()

    def test_get_watchers(self):
        self.hardware.get_watchers()
