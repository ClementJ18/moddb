from moddb import soup
from moddb.pages import Poll
import json

"""A version of the json file this script creates is cached on the repository, prioritize 
getting the data from there as opposed to rebuilding the file as it creates many requests for
moddb. Or at least download the file from the repository, update it and then create a PR."""

html = soup("https://www.moddb.com/polls")
with open("polls.json", "r") as f:
    cache = json.load(f)

#determine what pages need to be chached
page_total = int(html.find("div", class_="pages").find_all("a")[-1].string)
pages = page_total - cache.pop("pages", 0)

#get last registered option id
try:
    last_id = cache[list(cache.keys())[-1]][-1] + 1
except IndexError:
    last_id = 0

#iterate through pages from highest page number to lowest
#+2 because we want to iterate over the last page we iterated over in case there are new polls on it.
for page_num in reversed(range(1, pages + 2)):

    #get the page
    html = soup(f"https://www.moddb.com/polls/page/{page_num}")
    polls = html.find("div", class_="table").find_all("div", recursive=False)[1:]

    #iterate through all the polls present
    for poll in polls:
        poll = Poll(soup(poll.a["href"]))

        #if the poll has already been cached then we skip it
        if str(poll.id) in cache:
            continue

        #cache the new poll and increment
        new_last_id = last_id + len(poll.options)
        cache[str(poll.id)] = [x for x in range(last_id, new_last_id)]
        last_id = new_last_id

cache["pages"] = page_total
with open("polls.json", "w") as f:
    json.dump(cache, f)
