import bs4
import requests
import re
import time
import logging

logging.basicConfig(level=logging.INFO)

enum_dict = [
    {
        "name": "SoftwareCategory",
        "url": "https://www.moddb.com/software",
        "doc": "The category of the software",
        "key": "category"
    },
    {
        "name": "Difficulty",
        "url": "https://www.moddb.com/tutorials",
        "doc": "Difficulty of the tutorial",
        "key": "meta"
    },
    {
        "name": "TutorialCategory",
        "url": "https://www.moddb.com/tutorials",
        "doc": "Skill covered by the tutorial",
        "key": "subtype"
    },
    {
        "name": "GroupCategory",
        "url": "https://www.moddb.com/groups",
        "doc": "Category of fan groups",
        "key": "category"
    },
    {
        "name": "AddonCategory",
        "url": "https://www.moddb.com/addons",
        "doc": "Category of addons",
        "key": "category"
    },
    {
        "name": "Licence",
        "url": "https://www.moddb.com/addons",
        "doc": "The licence of the object",
        "key": "licence"
    },
    {
        "name": "Status",
        "url": "https://www.moddb.com/mods",
        "doc": "Status of a page",
        "key": "released"
    },
    {
        "name": "Theme",
        "url": "https://www.moddb.com/mods",
        "doc": "Theme of the page",
        "key": "theme"
    },
    {
        "name": "Genre",
        "url": "https://www.moddb.com/mods",
        "doc": "Genre of the page",
        "key": "genre"
    },
    {
        "name": "Scope",
        "url": "https://www.moddb.com/games",
        "doc": "Scope of the game",
        "key": "indie"
    },
    {
        "name": "FileCategory",
        "url": "https://www.moddb.com/downloads",
        "doc": "The category of the File",
        "key": "category"
    },
    {
        "name": "JobSkill",
        "url": "https://www.moddb.com/jobs",
        "doc": "The skill required for a job",
        "key": "skill"
    },
    {
        "name": "HardwareCategory",
        "url": "https://www.moddb.com/hardware",
        "doc": "The category of the hardware",
        "key": "category"
    },
    {
        "name": "SoftwareCategory",
        "url": "https://www.moddb.com/software",
        "doc": "The category of the software",
        "key": "category"
    },
]

def generate_member_list(html, enum):
    soup = bs4.BeautifulSoup(html, "html.parser")
    selects = soup.find("select", attrs={"name": enum["key"]}).find_all("option")
    max_size = 0

    names = []
    members = []
    for select in selects:
        if not select["value"]:
            continue
        
        name_raw = select.string.lower().replace("-", "").strip().replace("3d", "d3").replace("2d", "d2").replace("4x", "x4")
        name = re.sub(r'[\s\&\/\',]+', '_', name_raw)

        if name in names:
            name = f'sub_{name}'
        
        members.append((int(select["value"]), name))
        names.append(name)
        max_size = len(name) if len(name) > max_size else max_size

    logging.info("%s: size %s max size %s", enum["name"], len(members), max_size)
    logging.debug("%s: %s", len(selects), selects)
    return members, max_size

def generate_string(members, max_size, enum):
    string = f'class {enum["name"]}(enum.Enum):\n'
    string += f'    """{enum["doc"]}"""\n\n'
    for member in members:
        string += f"    {member[1]}{' '*(max_size - len(member[1]))} = {member[0]}\n"

    string += "\n\n"

    return string

def generate_enums(enums):
    string = "# GENERATED AUTOMATICALLY, DO NOT EDIT\n"
    with open("scripts/data/enums_base.txt", "r") as f:
        string += f.read()
    
    for enum in enums:
        r = requests.get(enum["url"])
        members, max_size = generate_member_list(r.text, enum)
        string += generate_string(members, max_size, enum)
        time.sleep(15)

    with open("moddb/enums.py", "w") as f:
        f.write(string)


if __name__ == '__main__':
    generate_enums(enum_dict)

