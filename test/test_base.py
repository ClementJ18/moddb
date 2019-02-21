import unittest
import moddb

from test.test_config import username, password

class TestFrontPage(unittest.TestCase):
    def setUp(self):
        self.fp = moddb.front_page()

    def get_articles(self):
        for article in self.fp.articles:
            article.parse()

    def get_games(self):
        for game in self.fp.games:
            game.parse()

    def get_files(self):
        for file in self.fp.files:
            file.parse()

class TestSearch(unittest.TestCase):
    def setUp(self):
        cat = getattr(self, "category", moddb.SearchCategory.mods)
        self.search= moddb.search(cat)

    def test_resort(self):
        results = self.search.results
        search2 = self.search.resort(("visitstotal", "asc"))
        self.assertNotEqual(results, search2.results)

    def test_next_page(self):
        self.search.next_page()

    def test_previous_pages(self):
        search = self.search.next_page()
        search.previous_page()

class TestParse(unittest.TestCase):
    def setUp(self):
        self.model = moddb.parse(getattr(self, "url", "https://www.moddb.com/mods/edain-mod"))

    def test_check(self):
        pass

class TestLogin(unittest.TestCase):
    def test_login(self):
        moddb.login(username, password)

    def test_fake_login(self):
        with self.assertRaises(ValueError):
            moddb.login("tico", "ticoisgod")
