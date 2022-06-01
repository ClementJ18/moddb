from ast import Import
import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

try:
    from tests.test_config import username, password
except ModuleNotFoundError:
    import os
    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

import moddb

DEFAULT_SEARCH = ("edain mod", moddb.SearchCategory.mods)

@patch("moddb.utils.request", new=patched_request)
class TestFrontPage:
    @pytest.fixture(autouse=True)
    def _get_object(self, request):
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

@patch("moddb.utils.request", new=patched_request)
class TestSearch:
    @pytest.fixture(params=[DEFAULT_SEARCH], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.search= moddb.search(request.param[1], query=request.param[0])

    def test_resort(self):
        results = self.search._results
        search2 = self.search.resort(("visitstotal", "asc"))
        assert results != search2._results

    def test_next_page(self):
        self.search.next_page()

    def test_previous_pages(self):
        search = self.search.next_page()
        search.previous_page()

class TestLogin:
    def test_login(self):
        moddb.login(username, password)

    def test_bad_login(self):
        with pytest.raises(ValueError) as e:
            moddb.login("tico", "ticoisgod")

    def tearDown(self):
        moddb.SESSION.close()
