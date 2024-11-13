import pytest

from moddb.utils import LOGIN_LIMITER
from tests.utils import sample_list

try:
    from tests.test_config import username, password
except ModuleNotFoundError:
    import os

    username = os.environ["USERNAME"]
    password = os.environ["PASSWORD"]

import moddb

DEFAULT_SEARCH = ("edain mod", moddb.SearchCategory.mods)
DEFAULT_TAG_SEARCH = "strategy"


@pytest.mark.vcr
class TestFrontPage:
    @pytest.fixture(autouse=True)
    def _get_object(self, request):
        self.fp = moddb.front_page()

    def test_get_articles(self):
        for article in sample_list(self.fp.articles, 3):
            article.parse()

    def test_get_games(self):
        for game in sample_list(self.fp.games, 3):
            game.parse()

    def test_get_files(self):
        for file in sample_list(self.fp.files, 3):
            file.parse()

    def test_get_poll(self):
        self.fp.get_poll()


@pytest.mark.vcr
class TestSearch:
    @pytest.fixture(params=[DEFAULT_SEARCH], autouse=True)
    def _get_object(self, request):
        self.search = moddb.search(request.param[1], query=request.param[0])

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
        LOGIN_LIMITER.reset()
        moddb.login(username, password)

    def test_bad_login(self):
        LOGIN_LIMITER.reset()
        with pytest.raises(ValueError):
            moddb.login("tico", "ticoisgod")

    def tearDown(self):
        moddb.SESSION.close()


@pytest.mark.vcr
class TestTagSearch:
    @pytest.fixture(params=[DEFAULT_TAG_SEARCH], autouse=True)
    def _get_object(self, request):
        self.search = moddb.search_tags(request.param)

    def test_resort(self):
        results = self.search._results
        search2 = self.search.resort(("visitstotal", "asc"))
        assert results != search2._results

    def test_next_page(self):
        self.search.next_page()

    def test_previous_pages(self):
        search = self.search.next_page()
        search.previous_page()
