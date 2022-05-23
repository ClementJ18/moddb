import unittest
import moddb

class TestPlatform(unittest.TestCase):
    def setUp(self):
        with open(getattr(self, "path", "test/fixtures/pc.html"), "r") as f:
            self.platform = moddb.pages.Platform(moddb.utils.soup(f.read()))

    def test_get_comments(self):
        self.platform.get_comments()
        self.platform.get_comments(4)

    def test_get_engines(self):
        engines = self.platform.get_engines()
        self.platform.get_engines(3)

        for engine in engines:
            engine.parse()

    def test_get_games(self):
        games = self.platform.get_games()
        self.platform.get_games(3)

        for game in games:
            game.parse()

    def test_get_hardware(self):
        hardwares = self.platform.get_hardware()
        self.platform.get_hardware(3)

        for hardware in hardwares:
            hardware.parse()

    def test_get_mods(self):
        mods = self.platform.get_mods()
        self.platform.get_mods(3)

        for mod in mods:
            mod.parse()

    def test_get_software(self):
        softwares = self.platform.get_software()
        self.platform.get_software(3)

        for software in softwares:
            software.parse() 
