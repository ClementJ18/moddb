import pytest

from tests.utils import sample_list

import moddb

DEFAULT = "https://www.moddb.com/software/project-neptune-vr"

pytestmark = [pytest.mark.vcr]


class TestSoftware:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.software = moddb.Software(moddb.get_page(request.param))

    def test_get_articles(self):
        articles = self.software.get_articles()
        self.software.get_articles(4)
        self.software.get_articles(category=moddb.ArticleCategory.news)

        for article in sample_list(articles, 3):
            article.parse()

    def test_get_comments(self):
        self.software.get_comments()
        self.software.get_comments(4)

    def test_get_files(self):
        files = self.software.get_files()
        self.software.get_files(4)
        self.software.get_files(category=moddb.FileCategory.demo)

        for file in sample_list(files, 3):
            file.parse()

    def test_get_images(self):
        images = self.software.get_images()

        for image in sample_list(images, 3):
            image.parse()

    def test_get_reviews(self):
        self.software.get_reviews()
        self.software.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.software.get_tutorials()
        self.software.get_tutorials(3)
        self.software.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in sample_list(tutorials, 3):
            tutorial.parse()

    def test_get_videos(self):
        videos = self.software.get_videos()

        for video in sample_list(videos, 3):
            video.parse()

    def test_get_watchers(self):
        self.software.get_watchers()

    def test_get_tags(self):
        tags = self.software.get_tags()
        # if tags:
        #     random.choice(tags)._get_members()
