# GENERATED AUTOMATICALLY, DO NOT EDIT
import enum


class SearchCategory(enum.Enum):
    """The list of things you can search for"""

    games = 0
    mods = 1
    addons = 2
    downloads = 3
    videos = 4
    articles = 5
    engines = 6
    developers = 7
    groups = 8
    forum = 9
    jobs = 10
    images = 11
    audio = 12
    reviews = 13
    headlines = 14
    blogs = 15
    hardwares = 16
    softwares = 17
    members = 18
    news = articles
    tutorials = articles
    companys = developers
    features = articles


class Category(enum.Enum):
    """Enum for the different areas of the site which things can be attached to"""

    mods = "mods"
    games = "games"
    engines = "engines"
    downloads = "downloads"


class RSSType(enum.Enum):
    """Enum to define the type of RSS you want to get from this page"""

    articles = 0
    downloads = 1
    images = 2
    videos = 3
    tutorials = 4
    reviews = 5
    addons = 6
    blogs = 7
    headlines = 8
    news = 9
    audio = 10
    jobs = 11
    poll = 12


class MediaCategory(enum.Enum):
    """What category a media object is, use for read purposes."""

    video = 0
    image = 1
    audio = 2


class ArticleCategory(enum.Enum):
    """Category of the article"""

    news = 1
    features = 2
    tutorials = 4


class Membership(enum.Enum):
    """Member ship settings of Groups and Teams"""

    invitation = 1
    application = 2
    open_to_all = 3


class TeamCategory(enum.IntFlag):
    """Category of companies, either publisher, developer or both"""

    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return self._name_
        members, uncovered = enum._decompose(cls, self._value_)
        return "|".join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    developer = 3
    publisher = 4


class ThumbnailType(enum.Enum):
    """The various types of thunbails that can be created"""

    mod = 0
    game = 1
    engine = 2
    member = 3
    group = 4
    article = 5
    review = 6
    team = 7
    blog = 8
    addon = 9
    file = 10
    job = 11
    platform = 12
    media = 13
    software = 14
    hardware = 15
    company = team


class PlayerStyle(enum.IntFlag):
    """The player style of the game"""

    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return self._name_
        members, uncovered = enum._decompose(cls, self._value_)
        return "|".join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    singleplayer = 1
    multiplayer = 2
    coop = 4
    mmo = 8


class TimeFrame(enum.Enum):
    """How recently the page was updated/uploaded, 24 hours, last week, last month, ect..."""

    day = 1
    week = 2
    month = 3
    year = 4
    more = 5


class WatchType(enum.Enum):
    mod = 0
    game = 1
    engine = 2
    group = 3
    member = 4


class Month(enum.Enum):
    january = "01"
    february = "02"
    march = "03"
    april = "04"
    may = "05"
    june = "06"
    july = "07"
    august = "08"
    september = "09"
    october = "10"
    november = "11"
    december = "12"


# BELOW THIS LINE ENUMS ARE GENERATED AUTOMATICALLY
# PR changes to scripts/generate_enums.py if you want to
# change something


class SoftwareCategory(enum.Enum):
    """The category of the software"""

    programming = 1
    ide = 2
    sdk = 3
    emulator = 4
    d3_art = 5
    d3_graphics = 6
    voxel_editor = 7
    normal_map_generator = 8
    uv_mapping_and_unwrapping = 9
    heightmap_or_terrain_generator = 10
    shader_editor = 11
    d2_art = 12
    raster_graphics_editor = 13
    vector_graphics_editor = 14
    sprite_editor_and_rigger = 15
    tile_or_map_editor = 16
    sound_and_music = 17
    audio_editing = 18
    digital_audio_workstation = 19
    music_sequencer = 20
    software_synthesizer = 21
    gaming = 22
    gaming_client = 23
    voip = 24
    overclocking = 25
    benchmarking = 26
    streaming_and_recording = 27
    web_pr_and_other = 28
    game_design = 29
    web_design = 30
    browser = 31
    social_networking = 32
    video_editing = 33
    vr = 34


class Difficulty(enum.Enum):
    """Difficulty of the tutorial"""

    basic = 1
    intermediate = 2
    advanced = 3


class TutorialCategory(enum.Enum):
    """Skill covered by the tutorial"""

    coding = 1
    client_side_coding = 16
    server_side_coding = 17
    graphics = 2
    ui_hud = 4
    textures = 5
    concept_art = 3
    level_design = 23
    mapping_technical = 6
    level_design_theory = 24
    modelling = 7
    players_modelling = 8
    weapons_modelling = 9
    props_modelling = 19
    animation = 10
    skinning = 11
    sound = 12
    sound_effects = 13
    voice_acting = 14
    music = 25
    general = 26
    pr = 18
    website = 21
    design_concepts = 31
    management = 15
    starting_a_mod = 32
    installers = 27
    server_tools = 28
    qa_testing = 29
    other = 30


class GroupCategory(enum.Enum):
    """Category of fan groups"""

    official = 1
    arts_literature = 4
    developer_publisher = 99
    educational = 2
    entertainment_press = 9
    event = 11
    fans_clans = 3
    geographic = 7
    hardware_tech = 5
    hobbies_interests = 6
    web_community = 10
    other = 8


class AddonCategory(enum.Enum):
    """Category of addons"""

    maps = 100
    multiplayer_map = 101
    singleplayer_map = 102
    prefabs = 103
    models = 104
    animal_model = 105
    players_model = 106
    prop_model = 132
    vehicle_model = 107
    weapons_model = 108
    models_pack = 131
    skins = 110
    animal_skin = 111
    players_skin = 112
    prop_skin = 133
    vehicle_skin = 113
    weapons_skin = 114
    skin_pack = 134
    audio = 116
    music = 117
    animal_audio = 135
    players_audio = 119
    vehicle_audio = 120
    weapons_audio = 121
    ambience_sounds = 137
    language_sounds = 138
    audio_pack = 118
    graphics = 123
    decals = 124
    effects_gfx = 136
    guis = 125
    huds = 126
    sprays = 127
    sprites = 128
    textures = 129


class Licence(enum.Enum):
    """The licence of the object"""

    bsd = 7
    commercial = 1
    creative_commons = 2
    gpl = 5
    lgpl = 6
    zlib = 9
    mit = 8
    proprietary = 3
    public_domain = 4


class Status(enum.Enum):
    """Status of a page"""

    released = 1
    early_access = 4
    coming_soon = 2
    unreleased = 3


class Theme(enum.Enum):
    """Theme of the page"""

    abstract = 18
    anime = 1
    antiquity = 14
    comedy = 2
    comic = 3
    education = 17
    fantasy = 4
    fighter = 5
    history = 15
    horror = 6
    mafia = 20
    medieval = 16
    movie = 7
    music = 21
    nature = 13
    noire = 19
    pirate = 22
    realism = 8
    scifi = 9
    survival = 23
    sport = 12
    war = 10
    western = 11


class Genre(enum.Enum):
    """Genre of the page"""

    action = 1
    first_person_shooter = 3
    third_person_shooter = 34
    tactical_shooter = 4
    fighting = 20
    arcade = 39
    stealth = 43
    adventure = 5
    sub_adventure = 2
    platformer = 19
    point_and_click = 40
    visual_novel = 50
    driving = 6
    racing = 7
    car_combat = 8
    rpg = 10
    role_playing = 11
    roguelike = 44
    hack_n_slash = 51
    party_based = 53
    strategy = 14
    real_time_strategy = 15
    real_time_shooter = 42
    real_time_tactics = 45
    turn_based_strategy = 16
    turn_based_tactics = 46
    tower_defense = 47
    grand_strategy = 49
    x4 = 48
    moba = 52
    sport = 18
    baseball = 13
    basketball = 17
    football = 21
    golf = 33
    hockey = 35
    soccer = 36
    wrestling = 37
    sub_sport = 26
    simulation = 22
    combat_sim = 24
    futuristic_sim = 25
    realistic_sim = 23
    puzzle = 27
    cinematic = 41
    educational = 38
    family = 31
    party = 29
    rhythm = 28
    virtual_life = 30
    sub_puzzle = 32


class Scope(enum.Enum):
    """Scope of the game"""

    aaa = 1
    indie = 2


class FileCategory(enum.Enum):
    """The category of the File"""

    releases = 1
    full_version = 2
    demo = 3
    patch = 4
    script = 28
    server = 5
    trainer = 29
    media = 6
    trailers = 7
    movies = 8
    music = 9
    audio = 25
    wallpapers = 10
    tools = 11
    audio_tool = 12
    archive_tool = 20
    graphics_tool = 13
    mapping_tool = 14
    modelling_tool = 15
    installer_tool = 16
    server_tool = 17
    plugin = 27
    ides = 18
    sdk = 19
    source_code = 26
    miscellaneous = 21
    guides = 22
    tutorials = 23
    language_pack = 30
    other = 24


class JobSkill(enum.Enum):
    """The skill required for a job"""

    artists = 1
    audio_music = 2
    human_resources = 3
    level_designers = 4
    management = 5
    marketing = 6
    programmers = 7
    public_relations = 8
    qa_testers = 9
    sales = 10
    web_other = 11


class HardwareCategory(enum.Enum):
    """The category of the hardware"""

    headset = 1
    haptics = 2
    controller = 3
    video = 4
    sound = 5


class SoftwareCategory(enum.Enum):
    """The category of the software"""

    programming = 1
    ide = 2
    sdk = 3
    emulator = 4
    d3_art = 5
    d3_graphics = 6
    voxel_editor = 7
    normal_map_generator = 8
    uv_mapping_and_unwrapping = 9
    heightmap_or_terrain_generator = 10
    shader_editor = 11
    d2_art = 12
    raster_graphics_editor = 13
    vector_graphics_editor = 14
    sprite_editor_and_rigger = 15
    tile_or_map_editor = 16
    sound_and_music = 17
    audio_editing = 18
    digital_audio_workstation = 19
    music_sequencer = 20
    software_synthesizer = 21
    gaming = 22
    gaming_client = 23
    voip = 24
    overclocking = 25
    benchmarking = 26
    streaming_and_recording = 27
    web_pr_and_other = 28
    game_design = 29
    web_design = 30
    browser = 31
    social_networking = 32
    video_editing = 33
    vr = 34
