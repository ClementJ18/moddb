import unittest
from tests.utils import patched_request
from unittest.mock import patch
import moddb
import logging

from tests.test_mod import TestMod
from tests.test_game import TestGame
from tests.test_engine import TestEngine
from tests.test_file import TestFile
from tests.test_addon import TestAddon
from tests.test_media import TestMedia
from tests.test_article import TestArticle
from tests.test_group import TestGroup
from tests.test_team import TestTeam
from tests.test_job import TestJob
from tests.test_member import TestMember
from tests.test_platform import TestPlatform
from tests.test_software import TestSoftware
from tests.test_hardware import TestHardware
from tests.test_poll import TestPoll
from tests.test_base import TestFrontPage, TestSearch, TestLogin # , TestParse
from tests.test_client import TestClient

logger = logging.getLogger('moddb')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

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

team_urls = [
    "https://www.moddb.com/company/wallace2anjos",
    "https://www.moddb.com/company/valve",
    "https://www.moddb.com/company/draignet",
    "https://www.moddb.com/company/left-4-dead-mods",
    "https://www.moddb.com/company/taleworlds",
    "https://www.moddb.com/company/belaruso500",
    "https://www.moddb.com/company/v1-infinity"
]

for url in team_urls:
    TestTeam.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestTeam))

job_urls = [
    "https://www.moddb.com/jobs/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game",
    "https://www.moddb.com/jobs/looking-for-3d-modeller-for-fast-past-shooting-game1",
    "https://www.moddb.com/jobs/revshareroyalty-3d-character-artist",
    "https://www.moddb.com/jobs/seeking-2d-uiux-artist-3d-weapon-modler-character-animator",
    "https://www.moddb.com/jobs/2d-top-down-shooter-artistanimator",
    "https://www.moddb.com/jobs/player-modeler-modeler1"
] 

for url in job_urls:
    TestJob.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestJob))

member_urls = [
    "https://www.moddb.com/members/mladen1996",
    "https://www.moddb.com/members/na3703168",
    "https://www.moddb.com/members/barneypan",
    "https://www.moddb.com/members/officialnecro",
    "https://www.moddb.com/members/yizhang",
    "https://www.moddb.com/members/thibault60",
    "https://www.moddb.com/members/intense",
    "https://www.moddb.com/members/hunter",
    "https://www.moddb.com/members/upstart",
]

for url in member_urls:
    TestMember.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestMember))

platform_urls = [
    "https://www.moddb.com/platforms/pc",
    "https://www.moddb.com/platforms/mac",
    "https://www.moddb.com/platforms/linux",
    "https://www.moddb.com/platforms/vr",
    "https://www.moddb.com/platforms/ar"
]

for url in platform_urls:
    TestPlatform.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestPlatform))

hardware_urls = [
    "https://www.moddb.com/hardware/htc-vive",
    "https://www.moddb.com/hardware/jaunt-vr",
    "https://www.moddb.com/hardware/the-free-space-omni",
    "https://www.moddb.com/hardware/sprintr",
    "https://www.moddb.com/hardware/osvr",
    "https://www.moddb.com/hardware/oculus-rift"
]

for url in hardware_urls:
    TestHardware.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestHardware))

software_urls = [
    "https://www.moddb.com/software/project-neptune-vr",
    "https://www.moddb.com/software/kinecttovr",
    "https://www.moddb.com/software/harfang-3d",
    "https://www.moddb.com/software/tilt-brush",
    "https://www.moddb.com/software/virtual-desktop",
    "https://www.moddb.com/software/project-neptune-vr",
    "https://www.moddb.com/software/geovisionary"
]

for url in software_urls:
    TestSoftware.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestSoftware))

poll_urls = [
    "https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods",
    "https://www.moddb.com/polls/if-you-had-to-choose-which-feature-would-you-like-implemented-the-most",
    "https://www.moddb.com/polls/default-v5-theme-should-be",
    "https://www.moddb.com/polls/what-is-your-plan-for-2017",
    "https://www.moddb.com/polls/should-moddb-focus-on-mods-only",
    "https://www.moddb.com/polls/prices-in-game-profiles"
]

for url in poll_urls:
    TestPoll.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestPoll))

suite.addTests(loader.loadTestsFromTestCase(TestFrontPage))
suite.addTests(loader.loadTestsFromTestCase(TestLogin))

test_urls = [
    "https://www.moddb.com/polls/total-conversions-vs-cosmetic-mods",
    "https://www.moddb.com/software/harfang-3d",
    "https://www.moddb.com/hardware/sprintr",
    "https://www.moddb.com/platforms/linux",
    "https://www.moddb.com/members/officialnecro",
    "https://www.moddb.com/jobs/looking-for-3d-modeller-for-fast-past-shooting-game1",
    "https://www.moddb.com/company/draignet",
    "https://www.moddb.com/groups/tanks",
    "https://www.moddb.com/news/the-challenge-of-adblock",
    "https://www.moddb.com/games/grave-matters/images/image-3",
    "https://www.moddb.com/addons/hl2dm-20b",
    "https://www.moddb.com/games/grofast-industries/downloads/linux-offline-version",
    "https://www.moddb.com/engines/unity",
    "https://www.moddb.com/games/battle-for-middle-earth-ii",
    "https://www.moddb.com/mods/edain-mod",
]

for url in test_urls:
    TestParse.url = url
    suite.addTests(loader.loadTestsFromTestCase(TestParse))

queries = [
    ("edain mod", moddb.SearchCategory.mods),
    ("battle for middle earth", moddb.SearchCategory.games),
    ("tanks", moddb.SearchCategory.groups)
]

for query in queries:
    TestSearch.query = query[0]
    TestSearch.category = query[1]
    suite.addTests(loader.loadTestsFromTestCase(TestSearch))

suite.addTests(loader.loadTestsFromTestCase(TestClient))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
# result = suite.debug()

