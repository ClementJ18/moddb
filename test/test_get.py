import unittest
import moddb

import logging
logger = logging.getLogger('moddb')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

class TestGets(unittest.TestCase):
    def test_get_mods(self):
        urls = [
            "https://www.moddb.com/mods/edain-mod",
            "https://www.moddb.com/mods/the-horse-lords-a-total-modification-for-bfme",
            "https://www.moddb.com/mods/third-age-total-war",
            "https://www.moddb.com/mods/ilty-re-back-to-earth",
            "https://www.moddb.com/mods/armory-world-of-warcraft",
            "https://www.moddb.com/mods/perisno",
            "https://www.moddb.com/mods/middle-earth-at-war",
            "https://www.moddb.com/mods/zeruel87-mod"
        ]

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.Mod(soup)

    def test_get_games(self):
        urls = [
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

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.Game(soup)

    def test_get_engines(self):
        urls = [
            "https://www.moddb.com/engines/source",
            "https://www.moddb.com/engines/cryengine-3",
            "https://www.moddb.com/engines/unity",
            "https://www.moddb.com/engines/simmetri",
            "https://www.moddb.com/engines/limon-engine",
            "https://www.moddb.com/engines/unknown",
            "https://www.moddb.com/engines/shmup-creator",
            "https://www.moddb.com/engines/limon-engine"
        ]

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.Engine(soup)

    def test_get_files(self):
        urls = [
            "https://www.moddb.com/games/pokemon-generations/downloads/pokegen-v2-launcher",
            "https://www.moddb.com/mods/hidden-source/downloads/hidden-source-beta-4b",
            "https://www.moddb.com/mods/third-age-total-war/downloads/third-age-total-war-30-part-1of2",
            "https://www.moddb.com/groups/scgames/downloads/bottom-defender-101",
            "https://www.moddb.com/games/shifting-dungeons/downloads/shifting-dungeons-update-1-mac-osx",
            "https://www.moddb.com/games/grofast-industries/downloads/linux-offline-version",
            "https://www.moddb.com/mods/cleric-mod-for-legend-farewell-edition-83/downloads/legend-farewell-edition-833-ultimate",
            "https://www.moddb.com/games/na1549814307/downloads/gdz-simulator",
            "https://www.moddb.com/mods/legend-farewell-edition/downloads/mercenary-dark-power"
        ]

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.File(soup)

    def test_get_addons(self):
        urls = [
            "https://www.moddb.com/games/grand-theft-auto-san-andreas/addons/superman-sa-beta-v10",
            "https://www.moddb.com/mods/brutal-doom/addons/project-brutality",
            "https://www.moddb.com/games/sudoku-e-sport-world-cup-2017/addons/collector-files",
            "https://www.moddb.com/addons/hl2dm-20b",
            "https://www.moddb.com/mods/call-of-chernobyl/addons/doctorx-dynamic-faction-relations",
            "https://www.moddb.com/mods/call-of-chernobyl/addons/arsenal-overhaul",
            "https://www.moddb.com/games/cc-generals-zero-hour/addons/usa-challenge",
            "https://www.moddb.com/games/axis-allies/addons/simple-vanilla-sai-buff"
        ]

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.Addon(soup)

    def test_get_medias(self):
        urls = [
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

        for url in urls:
            print(url)
            soup = moddb.utils.soup(url)
            moddb.pages.Media(soup)
