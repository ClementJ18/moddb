.. ModDB Reader documentation master file, created by
   sphinx-quickstart on Sat Nov  4 21:28:02 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


ModDB Reader
========================================

.. toctree::
   :maxdepth: 2

The Moddb-reader library is a scrapping library for the ModDB site which can scrape mod pages and game page (more later). The parsed pages are then returned as objects which are listed below in all their glory.



Page Class
===================

Represents the base class for a scrapped page. 

There should be no need to create any of these manually or call any. Any of the 
attributes could potentially be None if the detail isn't found on the page.

Attributes
----------
name : str
    Name of the Mod/Game
desc : str
    Short description of the Mod/Game
tags : list
    List of :class: `Tag`
url : str
    URL of the Mod/Game, the one supplied in the :func: parse_mod(url)
comment : str
    URL to the comment form for that Mod/Game
follow : str
    URL to follow the Mod/Game
suggestions : list
    List of :class: `Suggestion`
rank : str
    Rank of the Mod/Game
contact : str
    URL to contact the Development Team for the Mod
homepage : str
    URL to the homepage supplied by the Development Team for the Mod
share_link : None
    For future implementation of the share link, None at the moment
articles : list
    List of :class: `Article`
count : :class: `Count`
    The :class: `Count` which represent statistics on the Mod/Game
style : :class: `Style`
    The :class: `Style` which represents the different 'style' information gathered on the Mod/Game


