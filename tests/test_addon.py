import pytest
from unittest.mock import patch

from tests.test_utils import patched_request

import moddb

DEFAULT = "https://www.moddb.com/games/grand-theft-auto-san-andreas/addons/superman-sa-beta-v10"

@patch("moddb.utils.request", new=patched_request)
class TestAddon:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.addon = moddb.Addon(moddb.get_page(request.param))

    def test_get_comments(self):
        self.addon.get_comments()
        self.addon.get_comments(5)

    def test_get_mirrors(self):
        self.addon.get_mirrors()
