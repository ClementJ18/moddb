import pytest
from unittest.mock import patch

from tests.utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/mods/third-age-total-war/videos/rohan7"


@patch("moddb.utils.request", new=patched_request)
class TestMedia:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.media = moddb.Media(moddb.get_page(request.param))

    def test_get_comments(self):
        self.media.get_comments()
        self.media.get_comments(4)
