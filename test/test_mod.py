import unittest
import moddb

class TestMod(unittest.TestCase):
    def setUp(self):
        self.mod = moddb.pages.Mod(moddb.soup(getattr(self, "url", "https://www.moddb.com/mods/edain-mod")))

    def test_get_addons(self):
        addons = self.mod.get_addons()
        self.mod.get_addons(2)
        self.mod.get_addons(licence=moddb.Licence.public_domain)
        for addon in addons:
            addon.parse()


    def test_get_articles(self):
        articles = self.mod.get_articles()
        self.mod.get_articles(4)
        self.mod.get_articles(category=moddb.ArticleType.news)

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