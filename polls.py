from moddb import soup
from moddb.pages import Poll

import json

html = soup("https://www.moddb.com/polls")
with open("polls.json", "r") as f:
    cache = json.load(f)

#determine what pages need to be chached
page_total = int(html.find("div", class_="pages").find_all("a")[-1].string)
pages = page_total - cache.pop("pages")

#get last registered option id
try:
    last_id = cache[list(cache.keys())[-1]][-1] + 1
except IndexError:
    last_id = 0

#iterate through pages
for page_num in reversed(range(1, pages + 2)):
    html = soup(f"https://www.moddb.com/polls/page/{page_num}")
    polls = html.find("div", class_="table").find_all("div", recursive=False)[1:]
    for poll in polls:
        poll = Poll(soup(poll.a["href"]))
        if str(poll.id) in cache:
            continue

        new_last_id = last_id + len(poll.options)
        cache[str(poll.id)] = [x for x in range(last_id, new_last_id)]
        last_id = new_last_id

cache["pages"] = page_total
with open("polls.json", "w") as f:
    json.dump(cache, f)
