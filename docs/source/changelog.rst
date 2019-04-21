.. currentmodule:: moddb

Changelog
==========
The page attempt to keep a clear list of breaking/non-breaking changes and new features made to the libary.

.. contents:: Table of Contents
   :local:
   :backlinks: none

v0.7
-----
Bug Fixes
###########
* Links in comment content are now properly displayed as links rather than simply the domain name
* Changed get_all_results to return either ResultList or CommentList to allow for comment flattening

New Features
##############


v0.6
-----
Bug Fixes
###########
* :class:`.MissingComment` has been properly documented
* Fixed bug where parsing tutorial articles would raise a KeyError

New Features
##############
* :class:`.Search` now includes the current page of results stored as the attribute `page`
* New enum called :class:`.Month` used to filter :class:`.Poll` searches
* :class:`.CommentList` now includes the page of comments currently store (`page`) and the total amount of pages (`max_page`).
* :class:`.Client` has test cases
* New list-like class :class:`.ResultList` returned by most `get_` functions to allow easier navigation of results
* :class:`.Search` now behaves like a list
* :class:`.Search` and :class:`.CommentList` have access to get_all_results, an expensive call that iterates through all the pages of results available and returns a list of all the results. This does not return duplicate entries.
* Changelog begins
    