import unittest
import moddb
import logging

from test.test_mod import TestMod
from test.test_game import TestGame
from test.test_engine import TestEngine
from test.test_file import TestFile
from test.test_addon import TestAddon
from test.test_media import TestMedia
from test.test_article import TestArticle
from test.test_group import TestGroup
from test.test_team import TestTeam
from test.test_job import TestJob
from test.test_member import TestMember
from test.test_platform import TestPlatform
from test.test_software import TestSoftware
from test.test_hardware import TestHardware
from test.test_poll import TestPoll
from test.test_base import TestFrontPage, TestSearch, TestLogin # , TestParse
from test.test_client import TestClient

logger = logging.getLogger('moddb')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

loader = unittest.TestLoader()
suite  = unittest.TestSuite()



mod_paths = [
    "test/fixtures/edain-mod.html",
    "test/fixtures/the-horse-lords-a-total-modification-for-bfme.html",
    "test/fixtures/third-age-total-war.html",
    "test/fixtures/ilty-re-back-to-earth.html",
    "test/fixtures/armory-world-of-warcraft.html",
    "test/fixtures/perisno.html",
    "test/fixtures/middle-earth-at-war.html"
]

for path in mod_paths:
    TestMod.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestMod))

game_paths = [
    "test/fixtures/battle-for-middle-earth-ii-rise-of-the-witch-king.html",
    "test/fixtures/battle-for-middle-earth-ii.html",
    "test/fixtures/battle-for-middle-earth.html",
    "test/fixtures/mount-blade-warband.html",
    "test/fixtures/minecraft.html",
    "test/fixtures/zombie-treat.html",
    "test/fixtures/half-life.html",
    "test/fixtures/diablo-2-lod.html",
    "test/fixtures/car-chase-simulator.html",
    "test/fixtures/fated-kingdom.html"
]

for path in game_paths:
    TestGame.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestGame))

engine_paths = [
    "test/fixtures/sage-strategy-action-game-engine.html",
    "test/fixtures/source.html",
    "test/fixtures/cryengine-3.html",
    "test/fixtures/unity.html",
    "test/fixtures/simmetri.html",
    "test/fixtures/limon-engine.html",
    "test/fixtures/unknown.html",
    "test/fixtures/shmup-creator.html",
    "test/fixtures/limon-engine.html"
]

for path in engine_paths:
    TestEngine.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestEngine))

file_paths = [
    "test/fixtures/pokegen-v2-launcher.html",
    "test/fixtures/hidden-source-beta-4b.html",
    "test/fixtures/third-age-total-war-30-part-1of2.html",
    "test/fixtures/bottom-defender-101.html",
    "test/fixtures/shifting-dungeons-update-1-mac-osx.html",
    "test/fixtures/linux-offline-version.html",
    "test/fixtures/legend-farewell-edition-833-ultimate.html",
    "test/fixtures/gdz-simulator.html"
]

for path in file_paths:
    TestFile.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestFile))

addon_paths = [
    "test/fixtures/superman-sa-beta-v10.html",
    "test/fixtures/project-brutality.html",
    "test/fixtures/collector-files.html",
    "test/fixtures/hl2dm-20b.html",
    "test/fixtures/doctorx-dynamic-faction-relations.html",
    "test/fixtures/arsenal-overhaul.html",
    "test/fixtures/usa-challenge.html",
    "test/fixtures/simple-vanilla-sai-buff.html"
]

for path in addon_paths:
    TestAddon.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestAddon))

media_paths = [
    "test/fixtures/rohan7.html",
    "test/fixtures/pewdiepie-approved.html",
    "test/fixtures/movie-max-1.html",
    "test/fixtures/movie-max-1.html",
    "test/fixtures/doom-exp-15g-flamethrower.html",
    "test/fixtures/prophesy-of-pendor-39-official-trailer.html",
    "test/fixtures/new-dlc-released.html",
    "test/fixtures/the-gates-of-argonath.html",
    "test/fixtures/screenshot2.html",
    "test/fixtures/image-3.html",
    "test/fixtures/new-khergit-heavy-armor1.html",
    "test/fixtures/new-khergit-armors-will-be-included-in-the-next-patch.html",
    "test/fixtures/vlado32-fields-of-green.html",
    "test/fixtures/podcast-17-v41-interview-with-ges.html",
    "test/fixtures/vlado32-fields-of-green.html",
    "test/fixtures/podcast-17-v41-interview-with-ges.html",
    "test/fixtures/the-mummy-returns-complete-score-23-leaving-clues-sandcastles.html",
    "test/fixtures/recoil-tension.html"
]

for path in media_paths:
    TestMedia.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestMedia))

article_paths = [
    "test/fixtures/whats-happening-to-this-project-in-2019.html",
    "test/fixtures/new-intro-wip.html",
    "test/fixtures/the-challenge-of-adblock.html",
    "test/fixtures/d2multires.html",
    "test/fixtures/patient-2045-devlog-1-january-2019.html",
    "test/fixtures/dungeon-siege-skinning-contest.html",
    "test/fixtures/neon-knight-manual.html",
    "test/fixtures/alma1.html",
    "test/fixtures/katharsis-devlog-11.html"
] 

for path in article_paths:
    TestArticle.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestArticle)) 

group_paths = [
    "test/fixtures/humour-satire-parody.html",
    "test/fixtures/star-wars-empire-at-war-forces-of-corruption-mods.html",
    "test/fixtures/warhammer-40k-fans-group.html",
    "test/fixtures/tanks.html",
    "test/fixtures/moddb.html",
    "test/fixtures/dreamhack-activities.html",
    "test/fixtures/indie-game-contest-strasbourg-2016.html",
    "test/fixtures/custom-night.html",
    "test/fixtures/2013-mod-of-the-year-awards.html"
] 

for path in group_paths:
    TestGroup.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestGroup))

team_paths = [
    "test/fixtures/wallace2anjos.html",
    "test/fixtures/valve.html",
    "test/fixtures/draignet.html",
    "test/fixtures/left-4-dead-mods.html",
    "test/fixtures/taleworlds.html",
    "test/fixtures/belaruso500.html",
    "test/fixtures/v1-infinity.html"
]

for path in team_paths:
    TestTeam.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestTeam))

job_paths = [
    "test/fixtures/programmer-enviro-artist-audio-specialist-needed-to-expand-our-launched-game.html",
    "test/fixtures/looking-for-3d-modeller-for-fast-past-shooting-game1.html",
    "test/fixtures/revshareroyalty-3d-character-artist.html",
    "test/fixtures/seeking-2d-uiux-artist-3d-weapon-modler-character-animator.html",
    "test/fixtures/2d-top-down-shooter-artistanimator.html",
    "test/fixtures/player-modeler-modeler1.html"
] 

for path in job_paths:
    TestJob.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestJob))

member_paths = [
    "test/fixtures/mladen1996.html",
    "test/fixtures/na3703168.html",
    "test/fixtures/barneypan.html",
    "test/fixtures/officialnecro.html",
    "test/fixtures/yizhang.html",
    "test/fixtures/thibault60.html",
    "test/fixtures/intense.html",
    "test/fixtures/hunter.html",
    "test/fixtures/upstart.html",
]

for path in member_paths:
    TestMember.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestMember))

platform_paths = [
    "test/fixtures/pc.html",
    "test/fixtures/mac.html",
    "test/fixtures/linux.html",
    "test/fixtures/vr.html",
    "test/fixtures/ar.html"
]

for path in platform_paths:
    TestPlatform.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestPlatform))

hardware_paths = [
    "test/fixtures/htc-vive.html",
    "test/fixtures/jaunt-vr.html",
    "test/fixtures/the-free-space-omni.html",
    "test/fixtures/sprintr.html",
    "test/fixtures/osvr.html",
    "test/fixtures/oculus-rift.html"
]

for path in hardware_paths:
    TestHardware.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestHardware))

software_paths = [
    "test/fixtures/project-neptune-vr.html",
    "test/fixtures/kinecttovr.html",
    "test/fixtures/harfang-3d.html",
    "test/fixtures/tilt-brush.html",
    "test/fixtures/virtual-desktop.html",
    "test/fixtures/project-neptune-vr.html",
    "test/fixtures/geovisionary.html"
]

for path in software_paths:
    TestSoftware.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestSoftware))

poll_paths = [
    "test/fixtures/total-conversions-vs-cosmetic-mods.html",
    "test/fixtures/if-you-had-to-choose-which-feature-would-you-like-implemented-the-most.html",
    "test/fixtures/default-v5-theme-should-be.html",
    "test/fixtures/what-is-your-plan-for-2017.html",
    "test/fixtures/should-moddb-focus-on-mods-only.html",
    "test/fixtures/prices-in-game-profiles.html"
]

for path in poll_paths:
    TestPoll.path = path
    suite.addTests(loader.loadTestsFromTestCase(TestPoll))

suite.addTests(loader.loadTestsFromTestCase(TestFrontPage))
suite.addTests(loader.loadTestsFromTestCase(TestLogin))

test_paths = [
    "test/fixtures/total-conversions-vs-cosmetic-mods.html",
    "test/fixtures/harfang-3d.html",
    "test/fixtures/sprintr.html",
    "test/fixtures/linux.html",
    "test/fixtures/officialnecro.html",
    "test/fixtures/looking-for-3d-modeller-for-fast-past-shooting-game1.html",
    "test/fixtures/draignet.html",
    "test/fixtures/tanks.html",
    "test/fixtures/the-challenge-of-adblock.html",
    "test/fixtures/image-3.html",
    "test/fixtures/hl2dm-20b.html",
    "test/fixtures/linux-offline-version.html",
    "test/fixtures/unity.html",
    "test/fixtures/battle-for-middle-earth-ii.html",
    "test/fixtures/edain-mod.html",
]

for path in test_paths:
    TestParse.path = path
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

