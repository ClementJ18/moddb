# ModDB Reader

**This library is still WIP, the original library was very limited and just bad overall. I'm rewriting this entirely to be more object oriented in design and to allow to scrap the full site as objects.**

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
Check out the [documentation](link.com.here) for more information

## Finished Models
* Mod
* Game  
* Engine
* File
* Media
* Addon
* Article
* Blog
* User
* Team
* Group
* Job
* Search Page
* Front Page

## WIP Models
* Platforms
* Tutorial

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
 