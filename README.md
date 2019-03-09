# ModDB Reader
**Library is now stable**

The goal of the library is to be able to navigate ModDB purely programmatically through scraping and parsing of the various models present on the website. This is based off a command of my bot which can parse either a game or a mod, this command gave birth to the original library which was extremely limited in its abilities and only able to parse a few pages with inconsistencies. This library is a much more mature and professional attempt at the whole idea, adding on a much deeper understanding of OOP.

This library is still quite young and therefore any PR or Issues are welcome to raise any questions or concern you may have. Once you can navigate the whole site programmatically I might look into making use of the login system too allow users to make POST requests.  

## Basic Usage
The simplest way to use this library is to simply pass a ModDB url to the parse function and let the magic happen.
```py
import moddb
mod = moddb.parse("http://www.moddb.com/mods/edain-mod")
print(mod.name) #Edain Mod
```
The library tries to get the type of the url you are passing on its own but due to inconsistencies in the ModDB site this is not always correct, if you desire to be more specific you can pass a ThumbnailType to the function.
```py
import moddb
mod = moddb.parse("http://www.moddb.com/mods/edain-mod", page_type=moddb.ThumbnailType.mod)
print(mod.name) #Edain Mod
```

## Advanced Usage
Check out the [documentation](https://moddb.readthedocs.io) for more information

[Support](https://discord.gg/Ape8bZt)

## Models
* [x] Mod
* [x] Game  
* [x] Engine
* [x] File
* [x] Media
* [x] Addon
* [x] Article
* [x] Blog
* [x] User
* [x] Team
* [x] Group
* [x] Job
* [x] Search Page
* [x] Front Page
* [x] Platforms
* [x] Software
* [x] HardwAre

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full model. Mainly because that model is being displayed as a preview in another page. Not to confuse with Thumbnails, Thumbnails are only guaranteed to contain a name and url of the page.
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.
* **Thumbnails**: A very widely used model meant to represent models which are references but not expanded onto. Usually the model in question will only include a url and the name of the page. This is transformed into a thumbnail and the user can then parse it with the built-in method.

## Current :blobthonk:'s
### Polls
Polls can be parsed fine from any entry point as long as they contain a url, however the problem relies in allowing users to vote on those polls. Three things are required for a poll to be submitted:
* the poll url: easily obtainable since it is either the url of the page or included in the form
* the poll id: same, either it is included in the form as an hidden input or within the page's report button
* the option ids: herein lies the issue, poll option ids are only available in the form of a poll, not the page itself.

Only one poll can be present at a time on the forms and therefore for any poll that is not the currently used poll it would be impossible to vote on. At the moment the best entry point to the solution would be to get the poll, than return to the main page, check if the poll on the main page is the same and if it is then get all the option ids. Still, it feels like a waste to implement a method that would only be used for the latest poll. This is also only guaranteed if the user has not currently voted on the new poll as once voted on a poll form changes to simply a short summary of current poll stats.

In addition, I considered manually rebuilding the poll options by incrementing the ids but it appears that there are missing polls and therefore polls ids won't follow each other numerically. So long story short: there is no way to allow voting on polls at the moment.

### Post Requests
The question of post requests is a complicated one for a couple reasons. First of all, it is technically out of the scope of a scrapper which acts more as a bunch of GET statements rather than as a full API. However, the scope of the project is slightly different, stating that ideally, you should be able to fully emulate the moddb website using this library and a web framework. So it is reasonable to assume that POST requests would not be considered feature creep even though they are not necessary for functionality. 

The more troublesome question is one of ethic. Now, I'm no professional but I assume that ads scrapped by bots don't generate revenue, or that at least, it seems logical that a website would guarantee that advertisers get the most bang for their buck. In addition, it also seems a fair assumption, that while modders keep the site alive they also require the most server power per user when compared to viewers. Viewers will only need a couple pages generated, while modders may upload files and images, create new page, ect... So, a scrapper for GET requests doesn't seem too bad, it would only hit people interested in viewing moddb programmatically, not requiring that much processing power. However, a POST aspect would open up the website to mass spam, individual pages could be spammed with comments and a massive amount of mods, games, engines, ect.. could be created at once. Of course, it does technically fall upon the shoulders of the web developers to secure their own website, but ModDB despite its flaws and shortcoming is a website dear to me. Therefore, for now, the library will remain strictly a scrapper while I ponder upon the question.
