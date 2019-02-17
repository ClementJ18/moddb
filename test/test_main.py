import unittest

# from test.test_game import TestGame
from test.test_mod import TestMod

loader = unittest.TestLoader()
suite  = unittest.TestSuite()

mod_urls = [
    "https://www.moddb.com/mods/edain-mod",
    "https://www.moddb.com/mods/the-horse-lords-a-total-modification-for-bfme",
    "https://www.moddb.com/mods/third-age-total-war",
    "https://www.moddb.com/mods/ilty-re-back-to-earth",
    "https://www.moddb.com/mods/armory-world-of-warcraft",
    "https://www.moddb.com/mods/perisno",
    "https://www.moddb.com/mods/middle-earth-at-war",
    "https://www.moddb.com/mods/zeruel87-mod"
]

for url in mod_urls:
    TestMod.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestMod))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
