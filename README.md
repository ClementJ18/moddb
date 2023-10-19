# ModDB Reader
**Library is now stable**

The goal of the library is to be able to navigate ModDB purely programmatically through scraping and parsing of the various models present on the website. This is based off a command of my bot which can parse either a game or a mod, this command gave birth to the original library which was extremely limited in its abilities and only able to parse a few pages with inconsistencies. This library is a much more mature and professional attempt at the whole idea, adding on a much deeper understanding of OOP.

## Basic Usage
The simplest way to use this library is to simply pass a ModDB url to the parse function and let the magic happen.
```py
import moddb
mod = moddb.parse_page("http://www.moddb.com/mods/edain-mod")
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
* [x] Watchers
* [x] Tags

Maybe
* [ ] Messages
* [ ] Threads

## Glossary
* **Partial[Model]**: A version of the model which does not contain all the attributes of the full model. Mainly because that model is being displayed as a preview in another page. Not to confuse with Thumbnails, Thumbnails are only guaranteed to contain a name and url of the page.
* **Boxes**: Containers present on pages, a **div** tag which contains information around a certain theme and as such have been grouped into Box Models of such.
* **Pages**: Another name for Models.
* **Thumbnails**: A very widely used model meant to represent models which are references but not expanded onto. Usually the model in question will only include a url and the name of the page. This is transformed into a thumbnail and the user can then parse it with the built-in method.

## Development
The necessary dependencies are stored in requirements.txt and requirements-dev.txt and can be installed with the following command
```
python -m pip install -r requirements.txt -r requirements-dev.txt
```

## Testing
The testing is handled in two ways. There is a standard set of tests which are more lightweight, they test different entities of the library using one URL per entity. The second way is through the extended test suite. This extended test suite runs the standard test suite with multiple urls for each entity. This provides a better coverage but is also a lot more expensive to run and sometimes errors out because of ratelimits. 

In general, if you're just trying to do a sanity check on the library it is recommended to use the standard test set using the cassettes. This minimizes requests dones to the ModDB server and your chance of being ratelimited. 

* Standard Set: `pytest -k "not main" --record-mode=new_episodes`
* Full Set: `pytest -k "main" --record-mode=all`

Because tests in the suite grab the latest items from pages it is essentially not possible to have a zero request test. It is recommended to always run tests with at least the `new_episodes` record mode if you're planning to use the cassettes.

`grep -r -l Service Unavailable * | xargs rm`
