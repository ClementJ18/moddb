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

## Installing
This package is not available on Pypi but can still be installed using pip if you also have git installed. Else you will have to download the repository and instal using the setup.py script located at root. To install with pip

```
pip install -U git+git://github.com/ClementJ18/moddb.git@v0.7
```

## Uninstalling
To uninstall the package

```
pip uninstall moddb
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

Maybe
* [ ] Messages
* [ ] Threads

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
The question of post requests is a complicated one for a couple reasons. First of all, it is technically out of the scope of a scraper which acts more as a bunch of GET statements rather than as a full API. However, the scope of the project is slightly different, stating that ideally, you should be able to fully emulate the moddb website using this library and a web framework. So it is reasonable to assume that POST requests would not be considered feature creep even though they are not necessary for functionality. 

The more troublesome question is one of ethic. Now, I'm no professional but I assume that ads scrapped by bots don't generate revenue, or that at least, it seems logical that a website would guarantee that advertisers get the most bang for their buck. In addition, it also seems a fair assumption, that while modders keep the site alive they also require the most server power per user when compared to viewers. Viewers will only need a couple pages generated, while modders may upload files and images, create new page, ect... So, a scraper for GET requests doesn't seem too bad, it would only hit people interested in viewing moddb programmatically, not requiring that much processing power. However, a POST aspect would open up the website to mass spam, individual pages could be spammed with comments and a massive amount of mods, games, engines, ect.. could be created at once. Of course, it does technically fall upon the shoulders of the web developers to secure their own website, but ModDB despite its flaws and shortcoming is a website dear to me. Therefore, for now, the library will remain strictly a scraper while I ponder upon the question.

### Deleting comments
Requests related to comments have a `hash` field which seems to be a uuid. For adding comment, a simple random uuid v4 seems to do the trick, something I can easily generate myself. However, I have ran into a singuliar problem when trying to genereate a hash value for the field required for deleting comments. It seems not to be the same type, it might not even be a uuid at all. Parsing the various hashes has shown a random assortment of all versions of uuids, so it is unlikely it is actually one. Which leaves us with the problem of it being a hash, but a hash of what?

The hash is reloaded to a different one everytime the page is reloaded leading me to think that it might be linked to a timestamp. Currently, my approach is to try and figure out what the hash is, once I have but the smallest lead on what algorithm or what name it has I can easily dig that way until I manage to replicate the process. Here are the probable hashes:
- MD5
- NTLM
- MD4
- LM
- RAdmin v2.x
- Haval-128
- MD2
- RipeMD-128
- Tiger-128
- Snefru-128
- MD5(HMAC)
- MD4(HMAC)
- Haval-128(HMAC)
- RipeMD-128(HMAC)
- Tiger-128(HMAC)
- Snefru-128(HMAC)
- MD2(HMAC)
- MD5(ZipMonster)
- MD5(HMAC(Wordpress))
- Skein-256(128)
- Skein-512(128)

This would be a piece of cake if I knew what exactly was being hashed, but even that I don't know, perhaps some mix of the sitearea, site id, ect... It has an expiry date, so the starting point would probably by to figure out what the expiry date is in order to get a better idea of what the timestamp is.

Currently the following formats have been tried:
- hashlib.md5(str(time.time()+100000).encode('utf-8')).digest()
- hashlib.new("md4", str(time.time()+100000).encode('utf-8')).hexdigest()

The most efficient backup plan is as follows: add a new url field to the Comment object, which contains the precise location of where the comment came, with the shortcoming that the page might change if many comments are added. When the comment deletion is required, use the Client's session to re-retrieve the comment. Since it is assumed that the client has enough permissions it should mean that the comments will have a hash attribute, if it does not raise a permission error. If it does, retrieve it and proceed with the deletion. Issues with this remain that comments have a chance of moving around between the time period of the initial comment grab and of the time the user requests for the comment to be parsed.

It could also be that the token are just random tokens generated server side, added to a database and then discarded ~30 minutes later in which case there are no ways to fake those tokens.
