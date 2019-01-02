import enum

class SearchCategory(enum.Enum):
    games = 0
    mods = 1
    addons = 2
    dowloads = 3
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

class Category(enum.Enum):
    mods = "mods"
    games = "games"
    engines = "engines"
    downloads = "downloads"

class MediaCategory(enum.Enum):
    video = 0
    image = 1
    audio = 2

class ArticleType(enum.Enum):
    news = 1
    features = 2
    tutorials = 4

class Difficulty(enum.Enum):
    basic = 1
    intermidiate = 2
    advanced = 3

class TutorialType(enum.Enum):
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
    

class Membership(enum.Enum):
    invitation = 1
    application = 2
    open_to_all = 3

class TeamCategory(enum.Enum):
    developer = 3
    publisher = 4

class GroupCategory(enum.Enum):
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

class ThumbnailType(enum.Enum):
    mod = 0
    game = 1
    engine = 2
    user = 3
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
    company = team

class AddonCategory(enum.Enum):
    maps = 100
    models = 104
    skins = 110
    audio = 116
    graphics = 123
    multiplayer_map = 101
    singleplayer_map = 102
    prefabs = 103
    animal_model = 105
    players_model = 106
    prop_model = 132
    vehicle_model = 107
    weapons_model = 108
    models_pack = 131
    animal_skin = 111
    players_skin = 112
    prop_skin = 133
    vehicle_skin = 113
    weapons_skin = 114
    skin_pack = 134
    music = 117
    animal_audio = 135
    players_audio = 119
    vehicle_audio = 120
    weapons_audio = 121
    ambience_sounds = 137
    language_sounds = 138
    audio_pack = 118
    decals = 124
    effects_gfx = 136
    guis = 125
    huds = 126
    sprays = 127
    sprites = 128
    textures = 129

class Status(enum.Enum):
    released = 1
    unreleased = 3
    early_access = 4
    coming_soon = 2

class Theme(enum.Enum):
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
    sci_fi = 9
    survival = 23
    sport = 12
    war = 10
    western = 11
    
class Genre(enum.Enum):
    action = 1
    adventure = 5
    driving = 6
    rpg = 10
    strategy = 14
    sport = 18
    simulation = 22
    puzzle = 27
    first_person_shooter = 3
    third_person_shooter = 34
    tactical_shooter = 4
    fighting = 20
    arcade = 39
    stealth = 43
    platformer = 19
    point_and_click = 40
    visual_novel = 50
    racing = 7
    car_combat = 8
    role_playing = 11
    roguelike = 44
    hack_n_slash = 51
    party_based = 53
    real_time_strategy = 15
    real_time_shooter = 42
    real_time_tactics = 45
    turn_based_strategy = 16
    turn_based_tactics = 46
    tower_defense = 47
    grand_strategy = 49
    fourx = 48
    moba = 52
    baseball = 13
    basketball = 17
    football = 21
    golf = 33
    hockey = 35
    soccer = 36
    wrestling = 37
    combat_sim = 24
    futuristic_sim = 25
    realistic_sim = 23
    cinematic = 41
    educational = 38
    family = 31
    party = 29
    rhythm = 28
    virtual_life = 30

class PlayerStyle(enum.IntFlag):
    def __repr__(self):
        cls = self.__class__
        if self._name_ is not None:
            return self._name_
        members, uncovered = enum._decompose(cls, self._value_)
        return '|'.join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    singleplayer = 1
    multiplayer = 2
    coop = 4
    mmo = 8

class TimeFrame(enum.Enum):
    day = 1
    week = 2
    month = 3
    year = 4
    more = 5

class Licence(enum.Enum):
    bsd = 7
    commercial = 1
    creative_commons = 2
    gpl = 5
    l_gpl = 6
    zlib = 9
    mit = 8
    proprietary = 3
    public_domain = 4

class Scope(enum.Enum):
    aaa = 1
    indie = 2

class FileCategory(enum.Enum):
    releases = 1
    full_version = 2
    demo = 3
    patch = 4
    script = 28
    server = 5
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
    other = 24

class JobSkill(enum.Enum):
    artists = 1
    audio_or_music = 2
    human_resources = 3
    level_designers = 4
    management = 5
    marketing = 6
    programmers = 7
    public_relations = 8
    qa_or_testers = 9
    sales = 10
    web_or_other = 11
