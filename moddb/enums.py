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

class Difficulty(enum.Enum):
    """Difficulty of the tutorial"""
    basic = 1
    intermediate = 2
    advanced = 3

class TutorialCategory(enum.Enum):
    """Skill covered by the tutorial"""
    coding = 1
    graphics = 2
    concept_art = 3
    ui_hud = 4
    textures = 5
    mapping_technical = 6
    modelling = 7
    players_modelling = 8
    weapons_modelling = 9
    animation = 10
    skinning = 11
    sound = 12
    sound_effects = 13
    voice_acting = 14
    management = 15
    client_side_coding = 16
    server_side_coding = 17
    pr = 18
    props_modelling = 19
    website = 21
    level_design = 23
    level_design_theory = 24
    music = 25
    general = 26
    installers = 27
    server_tools = 28
    qa_testing = 29
    design_concepts = 31
    starting_a_mod = 32
    

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
        return '|'.join([str(m._name_ or m._value_) for m in members])

    __str__ = __repr__

    developer = 3
    publisher = 4

class GroupCategory(enum.Enum):
    """Category of fan groups"""
    official = 1
    educational = 2
    fans_clans = 3
    arts_literature = 4
    hardware_tech = 5
    hobbies_interests = 6
    geographic = 7
    other = 8
    entertainment_press = 9
    web_community = 10
    event = 11
    developer_publisher = 99

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

class AddonCategory(enum.Enum):
    """Category of addons"""
    maps = 100
    multiplayer_map = 101
    singleplayer_map = 102
    prefabs = 103
    models = 104
    animal_model = 105
    players_model = 106
    vehicle_model = 107
    weapons_model = 108
    skins = 110
    animal_skin = 111
    players_skin = 112
    vehicle_skin = 113
    weapons_skin = 114
    audio = 116
    music = 117
    audio_pack = 118
    players_audio = 119
    vehicle_audio = 120
    weapons_audio = 121
    graphics = 123
    decals = 124
    guis = 125
    huds = 126
    sprays = 127
    sprites = 128
    textures = 129
    models_pack = 131
    prop_model = 132
    prop_skin = 133
    skin_pack = 134
    animal_audio = 135
    effects_gfx = 136
    ambience_sounds = 137
    language_sounds = 138

class Status(enum.Enum):
    """Status of a page"""
    released = 1
    unreleased = 3
    early_access = 4
    coming_soon = 2

class Theme(enum.Enum):
    """Theme of the page"""
    anime = 1
    comedy = 2
    comic = 3
    fantasy = 4
    fighter = 5
    horror = 6
    movie = 7
    realism = 8
    sci_fi = 9
    war = 10
    western = 11
    sport = 12
    nature = 13
    antiquity = 14
    history = 15
    medieval = 16
    education = 17
    abstract = 18
    noire = 19
    mafia = 20
    music = 21
    pirate = 22
    survival = 23
    
class Genre(enum.Enum):
    """Genre of the page"""
    action = 1
    sub_adventure = 2
    first_person_shooter = 3
    tactical_shooter = 4
    adventure = 5
    driving = 6
    racing = 7
    car_combat = 8
    rpg = 10
    role_playing = 11
    baseball = 13
    strategy = 14
    real_time_strategy = 15
    turn_based_strategy = 16
    basketball = 17
    sport = 18
    platformer = 19
    fighting = 20
    football = 21
    simulation = 22
    realistic_sim = 23
    combat_sim = 24
    futuristic_sim = 25
    puzzle = 27
    rhythm = 28
    party = 29
    virtual_life = 30
    family = 31
    sub_puzzle = 32
    golf = 33
    third_person_shooter = 34
    hockey = 35
    soccer = 36
    wrestling = 37
    educational = 38
    arcade = 39
    point_and_click = 40
    cinematic = 41
    real_time_shooter = 42
    stealth = 43
    roguelike = 44
    real_time_tactics = 45
    turn_based_tactics = 46
    tower_defense = 47
    fourx = 48
    grand_strategy = 49
    visual_novel = 50
    hack_n_slash = 51
    moba = 52
    party_based = 53

class PlayerStyle(enum.IntFlag):
    """The player style of the game"""
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
    """How recently the page was updated/uploaded, 24 hours, last week, last month, ect..."""
    day = 1
    week = 2
    month = 3
    year = 4
    more = 5

class Licence(enum.Enum):
    """The licence of the object"""
    commercial = 1
    creative_commons = 2
    proprietary = 3
    public_domain = 4
    gpl = 5
    l_gpl = 6
    bsd = 7
    mit = 8
    zlib = 9

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
    server = 5
    media = 6
    trailers = 7
    movies = 8
    music = 9
    wallpapers = 10
    tools = 11
    audio_tool = 12
    graphics_tool = 13
    mapping_tool = 14
    modelling_tool = 15
    installer_tool = 16
    server_tool = 17
    ides = 18
    sdk = 19
    archive_tool = 20
    miscellaneous = 21
    guides = 22
    tutorials = 23
    other = 24
    audio = 25
    source_code = 26
    plugin = 27
    script = 28

class JobSkill(enum.Enum):
    """The skill required for q job"""
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

class HardwareCategory(enum.Enum):
    """The category of the hardware"""
    headset = 1
    haptics = 2
    controller = 3
    video = 4
    sound = 5

class SoftwareCategory(enum.Enum):
    """The category of the software"""
    commerical = 1
    communication = 2
    development = 3
    educational = 4
    entertainment = 5
    media = 6
    architecture = 7
    retail = 8
    tours = 9
    browser = 10
    social_networking = 11
    editor = 12
    sdk = 13
    sub_educational = 14
    environment_mapping = 15
    medical = 16
    simulation = 17
    adult = 18
    books = 19
    movies = 20
    sport = 21
    audio_recording_editing = 22
    video_capture_editing = 23
    motion_capture = 24
    graphics_editing = 25
    music = 26
    games = 27
