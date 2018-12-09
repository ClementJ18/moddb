# ModDB Reader

**This library is still WIP, the original library was very limited and just bad overall. I'm rewriting this entirely to be more object oriented in design and to allow to scrap the full site as objects.**

The goal of the library is to be able to navigate ModDB purely programmatically through scraping and parsing of the various models present on the website. This is based off a command of my bot which can parse either a game or a mod, this command gave birth to the original library which was extremely limited in its abilities and only able to parse a few pages with inconsistencies. This library is a much more mature and professional attempt at the whole idea, adding on a much deeper understanding of OOP.

This library is still quite young and therefore any PR or Issues are welcome to raise any questions or concern you may have. Once you can navigate the whole site programmatically I might look into making use of the login system too allow users to make POST requests.  

## Basic Utilization
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

## WIP Models
* Job
* Front Page
* Search Page

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full mode. Mainly because that model is being displayed as a preview in another page
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.

## Logging
This package makes use of the powerful Python logging module. Whenever the scrapper is unable to find a specific field for a model, either because it does not exist or because the scrapper cannot see it with its current permissions, then it will log it as an info. All logs will be sent to the `moddb` logger, to have access to the stream of logs you can do things like:
```py
import logging

logging.basicConfig(level=logging.INFO)
```
or
```py
import logging

logger = logging.getLogger('moddb')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
```

## Account
This package allows users to login into ModDB in order to have access to additional information which Guest users (the account the package uses by default) cannot see such as Guest comments waiting for approval or private groups/members. In order to login simply use the built-in library method
```py
import moddb
moddb.login("valid_username", "valid_password")
```

The session the package uses will be updated and all further requests will now be made logged in as that user. The function will raise a ValueError if the login fails. You can also log out of the account to disable access to those restricted elements with the `logout` function:
```
import moddb
moddb.logout()
```
