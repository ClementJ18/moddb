import unittest
import moddb

class TestSoftware(unittest.TestCase):
    def setUp(self):
        self.software = moddb.pages.Software(moddb.get_page(getattr(self, "url", "https://www.moddb.com/software/project-neptune-vr")))

    def test_get_articles(self):
        articles = self.software.get_articles()
        self.software.get_articles(4)
        self.software.get_articles(category=moddb.ArticleCategory.news)

        for article in articles:
            article.parse()

    def test_get_comments(self):
        self.software.get_comments()
        self.software.get_comments(4)

    def test_get_files(self):
        files = self.software.get_files()
        self.software.get_files(4)
        self.software.get_files(category=moddb.FileCategory.demo)

        for file in files:
            file.parse()

    def test_get_images(self):
        images = self.software.get_images()

        for image in images[:10]:
            image.parse()

    def test_get_reviews(self):
        self.software.get_reviews()
        self.software.get_reviews(3)

    def test_get_tutorials(self):
        tutorials = self.software.get_tutorials()
        self.software.get_tutorials(3)
        self.software.get_tutorials(difficulty=moddb.Difficulty.basic)

        for tutorial in tutorials:
            tutorial.parse()

    def test_get_videos(self):
        videos = self.software.get_videos()

        for video in videos:
            video.parse()
