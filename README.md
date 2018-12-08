# ModDB Reader

**This library is still WIP, the original library was very limited and just bad overall. I'm rewriting this entirely to be more object oriented in design and to allow to scrap the full site as objects.**

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

## WIP Models
* Team
* Group
* Job

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full mode. Mainly because that model is being displayed as a preview in another page
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.

## Logging
This package makes use of the powerful Python logging module. Whenever the scrapper is unable to find a specific field for a model, either because it does not exist or because the scrapper cannot see it with its current permissions, then it will log it as an info. All logs will be sent to the `moddb` logger, to have access to the stream of logs you can do things like:
```
import logging

logging.basicConfig(level=logging.INFO)
```
or
```
import logging

logger = logging.getLogger('moddb')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
```

## Account
This package allows users to login into ModDB in order to have access to additional information which Guest users (the account the package uses by default) cannot see such as Guest comments waiting for approval or private groups/members. In order to login simply use the built-in library method
```
import moddb
moddb.login("valid_username", "valid_password")
```

The session the package uses will be updated and all further requests will now be made logged in as that user. The function will raise a ValueError if the login fails.
