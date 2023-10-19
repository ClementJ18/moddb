import pytest

import moddb

DEFAULT = "https://www.moddb.com/mods/edain-mod/news/edain-46-tower-defense"

pytestmark = [pytest.mark.vcr]


class TestArticle:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.article = moddb.Article(moddb.get_page(request.param))

    def test_get_comments(self):
        self.article.get_comments()
        self.article.get_comments(4)
