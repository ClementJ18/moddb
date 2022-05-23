# ModDB Reader
**Library is now stable**

The goal of the library is to be able to navigate ModDB purely programmatically through scraping and parsing of the various models present on the website. This is based off a command of my bot which can parse either a game or a mod, this command gave birth to the original library which was extremely limited in its abilities and only able to parse a few pages with inconsistencies. This library is a much more mature and professional attempt at the whole idea, adding on a much deeper understanding of OOP.

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

## Installing
You can get it from pypi: https://pypi.org/project/moddb

```
pip install moddb
```

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
* [x] Updates
* [x] Friend Requests
* [ ] Watchers
* [ ] Tags

Maybe
* [ ] Messages
* [ ] Threads

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full model. Mainly because that model is being displayed as a preview in another page. Not to confuse with Thumbnails, Thumbnails are only guaranteed to contain a name and url of the page.
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.
* **Thumbnails**: A very widely used model meant to represent models which are references but not expanded onto. Usually the model in question will only include a url and the name of the page. This is transformed into a thumbnail and the user can then parse it with the built-in method.
