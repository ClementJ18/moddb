import unittest

from test.test_game import TestGame
from test.test_mod import TestMod
from test.test_engine import TestEngine
from test.test_file import TestFile
from test.test_addon import TestAddon
from test.test_media import TestMedia
from test.test_article import TestArticle
from test.test_group import TestGroup

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

game_urls = [
    "https://www.moddb.com/games/battle-for-middle-earth-ii-rise-of-the-witch-king",
    "https://www.moddb.com/games/battle-for-middle-earth-ii",
    "https://www.moddb.com/games/battle-for-middle-earth",
    "https://www.moddb.com/games/mount-blade-warband",
    "https://www.moddb.com/games/minecraft",
    "https://www.moddb.com/games/zombie-treat",
    "https://www.moddb.com/games/spellhack",
    "https://www.moddb.com/games/half-life",
    "https://www.moddb.com/games/diablo-2-lod",
    "https://www.moddb.com/games/car-chase-simulator",
    "https://www.moddb.com/games/project-harpy",
    "https://www.moddb.com/games/fated-kingdom"
]

for url in game_urls:
    TestGame.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestGame))

engine_urls = [
    "https://www.moddb.com/engines/sage-strategy-action-game-engine",
    "https://www.moddb.com/engines/source",
    "https://www.moddb.com/engines/cryengine-3",
    "https://www.moddb.com/engines/unity",
    "https://www.moddb.com/engines/simmetri",
    "https://www.moddb.com/engines/limon-engine",
    "https://www.moddb.com/engines/unknown",
    "https://www.moddb.com/engines/shmup-creator",
    "https://www.moddb.com/engines/limon-engine"
]

for url in engine_urls:
    TestEngine.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestEngine))

file_urls = [
    "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher",
    "https://www.moddb.com/mods/hidden-source/downloads/hidden-source-beta-4b",
    "https://www.moddb.com/mods/third-age-total-war/downloads/third-age-total-war-30-part-1of2",
    "https://www.moddb.com/groups/scgames/downloads/bottom-defender-101",
    "https://www.moddb.com/games/shifting-dungeons/downloads/shifting-dungeons-update-1-mac-osx",
    "https://www.moddb.com/games/grofast-industries/downloads/linux-offline-version",
    "https://www.moddb.com/mods/cleric-mod-for-legend-farewell-edition-83/downloads/legend-farewell-edition-833-ultimate",
    "https://www.moddb.com/games/na1549814307/downloads/gdz-simulator"
]

for url in file_urls:
    TestFile.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestFile))

addon_urls = [
    "https://www.moddb.com/games/grand-theft-auto-san-andreas/addons/superman-sa-beta-v10",
    "https://www.moddb.com/mods/brutal-doom/addons/project-brutality",
    "https://www.moddb.com/games/sudoku-e-sport-world-cup-2017/addons/collector-files",
    "https://www.moddb.com/addons/hl2dm-20b",
    "https://www.moddb.com/mods/call-of-chernobyl/addons/doctorx-dynamic-faction-relations",
    "https://www.moddb.com/mods/call-of-chernobyl/addons/arsenal-overhaul",
    "https://www.moddb.com/games/cc-generals-zero-hour/addons/usa-challenge",
    "https://www.moddb.com/games/axis-allies/addons/simple-vanilla-sai-buff"
]

for url in addon_urls:
    TestAddon.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestAddon))

media_urls = [
    "https://www.moddb.com/mods/third-age-total-war/videos/rohan7",
    "https://www.moddb.com/games/erie/videos/pewdiepie-approved",
    "https://www.moddb.com/games/the-last-tinker-city-of-colors/videos/movie-max-1",
    "https://www.moddb.com/games/dawns-light/videos/movie-max-1",
    "https://www.moddb.com/mods/doom-exp/videos/doom-exp-15g-flamethrower",
    "https://www.moddb.com/mods/saxondragon/videos/prophesy-of-pendor-39-official-trailer",
    "https://www.moddb.com/mods/extreme-vs-full-boost-mod/images/new-dlc-released",
    "https://www.moddb.com/mods/third-age-total-war/images/the-gates-of-argonath",
    "https://www.moddb.com/games/panoramical/images/screenshot2",
    "https://www.moddb.com/games/grave-matters/images/image-3",
    "https://www.moddb.com/mods/calradia-1417/images/new-khergit-heavy-armor1",
    "https://www.moddb.com/mods/calradia-1417/images/new-khergit-armors-will-be-included-in-the-next-patch",
    "https://www.moddb.com/mods/tiberium-essence/videos/vlado32-fields-of-green",
    "https://www.moddb.com/mods/goldeneye-source/videos/podcast-17-v41-interview-with-ges",
    "https://www.moddb.com/mods/tiberium-essence/videos/vlado32-fields-of-green",
    "https://www.moddb.com/mods/goldeneye-source/videos/podcast-17-v41-interview-with-ges",
    "https://www.moddb.com/mods/war-of-the-gods-wrath-of-egypt/videos/the-mummy-returns-complete-score-23-leaving-clues-sandcastles",
    "https://www.moddb.com/mods/recovered-operations/videos/recoil-tension"
]

for url in media_urls:
    TestMedia.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestMedia))

article_urls = [
    "https://www.moddb.com/mods/the-consequence-of-infection/news/whats-happening-to-this-project-in-2019",
    "https://www.moddb.com/mods/project-zer0/news/new-intro-wip",
    "https://www.moddb.com/news/the-challenge-of-adblock",
    "https://www.moddb.com/groups/editors/news/d2multires",
    "https://www.moddb.com/games/patient-2045/news/patient-2045-devlog-1-january-2019",
    "https://www.moddb.com/news/dungeon-siege-skinning-contest",
    "https://www.moddb.com/games/neon-knigh/tutorials/neon-knight-manual",
    "https://www.moddb.com/games/fear/tutorials/alma1",
    "https://www.moddb.com/games/katharsis/news/katharsis-devlog-11"
] 

for url in article_urls:
    TestArticle.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestArticle)) 

group_urls = [
    "https://www.moddb.com/groups/humour-satire-parody",
    "https://www.moddb.com/groups/star-wars-empire-at-war-forces-of-corruption-mods",
    "https://www.moddb.com/groups/warhammer-40k-fans-group",
    "https://www.moddb.com/groups/tanks",
    "https://www.moddb.com/groups/moddb",
    "https://www.moddb.com/groups/dreamhack-activities",
    "https://www.moddb.com/groups/indie-game-contest-strasbourg-2016",
    "https://www.moddb.com/groups/custom-night",
    "https://www.moddb.com/groups/2013-mod-of-the-year-awards"
] 

for url in group_urls:
    TestGroup.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestGroup))


runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
