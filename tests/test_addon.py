import pytest

import moddb

import pytest_vcr_delete_on_fail

DEFAULT = "https://www.moddb.com/games/grand-theft-auto-san-andreas/addons/superman-sa-beta-v10"

pytestmark = [pytest.mark.vcr, pytest.mark.vcr_delete_on_fail]


class TestAddon:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        self.addon = moddb.Addon(moddb.get_page(request.param))

    def test_get_comments(self):
        self.addon.get_comments()
        self.addon.get_comments(5)

    def test_get_mirrors(self):
        self.addon.get_mirrors()
