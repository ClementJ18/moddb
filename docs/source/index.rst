.. moddb documentation master file, created by
   sphinx-quickstart on Fri Dec 28 17:23:26 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. currentmodule:: moddb


Welcome to moddb's documentation!
=================================
.. image:: https://readthedocs.org/projects/moddb/badge/?version=latest
   :target: https://moddb.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: Licence: MIT

.. image:: https://img.shields.io/github/issues/ClementJ18/moddb.svg
   :target: https://github.com/ClementJ18/moddb/issues
   :alt: Open Issues

.. image:: https://img.shields.io/github/issues-pr/ClementJ18/moddb.svg
   :target: https://github.com/ClementJ18/moddb/pulls
   :alt: Open PRs

.. image:: https://img.shields.io/github/release/ClementJ18/moddb.svg
   :alt: Latest Release

.. image:: https://img.shields.io/github/stars/ClementJ18/moddb.svg?label=Stars&style=social 
   :target: https://github.com/ClementJ18/moddb

.. image:: https://img.shields.io/discord/389039439487434752.svg
   :target: https://discord.gg/Ape8bZt

.. image:: https://img.shields.io/github/commits-since/ClementJ18/moddb/latest.svg
    :target: https://github.com/ClementJ18/moddb/releases/latest

The moddb python library is a module to scrape the ModDB.com website. The goal is to emulate
the moddb website using function and OOP as if ModDB was simply an API. Ideally, in it's finished
state you should be able to pair with a web framework to perfectly emulate the website and all
its features.

.. contents:: Table of Contents
   :local:
   :backlinks: none

Basic Usage
------------

The simplest way to use this library is to simply pass a ModDB url to the parse function and let the magic happen:: 

   import moddb
   mod = moddb.parse("http://www.moddb.com/mods/edain-mod")
   print(mod.name) #Edain Mod

The library tries to get the type of the url you are passing on its own but due to inconsistencies in the ModDB site this is not always correct, if you desire to be more specific you can pass a ThumbnailType to the function:: 

   import moddb
   mod = moddb.parse(
               "http://www.moddb.com/mods/edain-mod", 
               page_type=moddb.ThumbnailType.mod
            )
   print(mod.name) #Edain Mod

Advanced Usage
---------------
Of course, relying on the library isn't always what we want, you'd be forced to use requests plus nothing's perfect and errors might occur. In some cases, you might benefit from having a finer control upon the process, in which case, it is good to know that you can easily do this with few additional imports. Given you suddenly want to use something like aiohttp to get the pages you could easily do something like this:: 

   import moddb
   import aiohttp

   async def get_page():
      async with aiohttp.ClientSession() as session:
         async with session.get("http://www.moddb.com/mods/edain-mod") as response:
            soup = moddb.soup(await r.text())

      return moddb.Mod(soup)

This would return a mod object, with you only having to import the bit you want to change from the original library, in that case aiohttp. This is not fully supported for all things however, for example trying to get the articles for that mod page you would be forced to completly parse the result page on your own or be forced to use requests.

See more snippets there: :ref:`snippets-ref`.


Searching
----------

The package supports searching moddb with an optional query, filters and to sort those results. Filters differ widely depending on which model is being searched therefore a good read of the documentation of the search function is recommended. The only required parameter of the search function is a valid moddb.SearchCategory as the first argument. All other arguments are optional. the `search` function returns a moddb.Search object. The most basic example is:: 

   from moddb import search, SearchCategory
   search = search(SearchCategory.mods)
   #returns a search objects with the results being a 
   #list of mod thumbnails

You can also search titles of the models with a string query:: 

   from moddb import search, SearchCategory
   search = search(SearchCategory.mods, query="age of the ring")
   #returns a search objects with the results being a list of 
   #mod thumbnails which moddb has matched with the words age of the ring

Many additional filters are available and listed in the documentation, each filter kwarg will expected a specific enum. The only exception is the game filters which expects either a game object or a moddb.Object with an id attribute. For example if we want to search for a released fantasy mod::

   from moddb import search, SearchCategory, Theme, Status
   search = search(SearchCategory.mods, 
         theme=Theme.fantasy, released=Status.released
      )
   #returns a search objects with the results being a list of mod 
   #thumbnails of mods which have been released and are labelled as 
   #fantasy themed.

And finally, you can sort the results with the `sort` kwargs which expects a tuple with the first element being a sort category which is valid for the model you're sorting for and the second being whether you want the sort to be ascending or descending::

   from moddb import search, SearchCategory, Sort
   search = search(SearchCategory.mods, sort=("rating", "asc"))
   #returns a search objects with the results being a list of mod 
   #thumbnails sorted by rating with highest rating first

Logging
--------

This package makes use of the powerful Python logging module. Whenever the scrapper is unable to find a specific field for a model, either because it does not exist or because the scrapper cannot see it with its current permissions, then it will log it as an info. All logs will be sent to the `moddb` logger, to have access to the stream of logs you can do things like::

   import logging
   logging.basicConfig(level=logging.INFO)

or::

   import logging
   logger = logging.getLogger('moddb')
   logger.setLevel(logging.INFO)
   handler = logging.FileHandler(filename='moddb.log', encoding='utf-8', mode='w')
   handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
   logger.addHandler(handler)

Account
--------

This package allows users to login into ModDB in order to have access to additional information which Guest users (the account the package uses by default) cannot see such as Guest comments waiting for approval or private groups/members. In order to login simply use the built-in library method::

   import moddb
   moddb.login("valid_username", "valid_password")

The session the package uses will be updated and all further requests will now be made logged in as that user. The function will raise a ValueError if the login fails. You can also log out of the account to disable access to those restricted elements with the `logout` function::

   import moddb
   moddb.logout()

Installing
------------
This package is not available on Pypi but can still be installed using pip if you also have git installed. Else you will have to download the repository and instal using the setup.py script located at root. To install with pip:: 

    pip install -U git+git://github.com/ClementJ18/moddb.git@v0.4

Uninstalling
-------------
To uninstall the package:: 

    pip uninstall moddb


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   filtering&sorting
   snippets
   base
   pages
   boxes
   client
   utils
   enums
