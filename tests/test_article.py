import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/mods/edain-mod/news/edain-46-tower-defense"

@patch("moddb.utils.request", new=patched_request)
class TestArticle:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.article = moddb.Article(moddb.get_page(request.param))
    
    def test_get_comments(self):
        self.article.get_comments()
        self.article.get_comments(4)
