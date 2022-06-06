import pytest
from unittest.mock import patch

from tests.test_utils import patched_request, sample_list

import moddb

DEFAULT = "https://www.moddb.com/platforms/pc"


@patch("moddb.utils.request", new=patched_request)
class TestPlatform:
    @pytest.fixture(params=[DEFAULT], autouse=True)
    def _get_object(self, request):
        with patch("moddb.utils.request", new=patched_request) as f:
            self.platform = moddb.Platform(moddb.get_page(request.param))

    def test_get_comments(self):
        self.platform.get_comments()
        self.platform.get_comments(4)

    def test_get_engines(self):
        engines = self.platform.get_engines()
        self.platform.get_engines(3)

        for engine in sample_list(engines, 3):
            engine.parse()

    def test_get_games(self):
        games = self.platform.get_games()
        self.platform.get_games(3)

        for game in sample_list(games, 3):
            game.parse()

    def test_get_hardware(self):
        hardwares = self.platform.get_hardware()
        self.platform.get_hardware(3)

        for hardware in sample_list(hardwares, 3):
            hardware.parse()

    def test_get_mods(self):
        mods = self.platform.get_mods()
        self.platform.get_mods(3)

        for mod in sample_list(mods, 3):
            mod.parse()

    def test_get_software(self):
        softwares = self.platform.get_software()
        self.platform.get_software(3)

        for software in sample_list(softwares, 3):
            software.parse()
