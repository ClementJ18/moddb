import pytest
from unittest.mock import patch
from tests.test_engine import DEFAULT

from tests.test_utils import patched_request

import moddb

DEFAULT = (
    "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher"
)


@patch("moddb.utils.request", new=patched_request)
class TestFile:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.file = moddb.File(moddb.get_page(request.param))

    def test_get_comments(self):
        self.file.get_comments()
        self.file.get_comments(5)
