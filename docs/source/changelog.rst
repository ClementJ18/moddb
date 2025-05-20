.. currentmodule:: moddb

Changelog
==========
The page attempt to keep a clear list of breaking/non-breaking changes and new features made to the libary.

.. contents:: Table of Contents
   :local:
   :backlinks: none

v0.13.0
-----------
Bug Fixes
###########
* Renamed `base.search` `category` parameter to `search_category` to avoid conflict with filters
* Fixed the way IDs are retrieved
* Fixed a bug where saving files and medias would not stream the response

New Features
##############
* `File` and `Addon` now have a `location` value that contains the location list of the entity
* `File.save`, `Addon.save` and `Media.save` can now take `chunk_size` as a keyword parameter to define the size of the chunks to stream in

v0.12.0
-------
Bug Fixes
##########
* Fixed SSL block

v0.11.0
-------
Bug Fixes
##########
* Fixed an edge case in comment parsing

New Features
#############
* Added `FrontPage.get_poll` to get the poll on the front page
* Ratelimiting login request to to 1/5s
* Ratelimited requests that are asked to raise will now raise `moddb.errors.Ratelimited`
* Profiles now display the aggregated download count of mods and games (if they have one) under `download_count`


Removed Features
#################
* Removed `FrontPage.poll` to reduce the number of requests used when calling `front_page()`


v0.10.0
-------
Bug Fixes
##########
* Pinned major releases of all dependencies
* Fixed improper parsing of not yet released pages
* Fixed improper parsing of get_tags when page did not have more tags

New Features
#############
* Documented more of the utility functions
* Some enum members have been renamed to better fit with the naming pattern of the website
* Tests now produce cassettes for easy re-use.

Removed Features
#################


v0.9.0
-------
Bug Fixes
##########

New Features
#############
* New object `Tag` representing tags
* New methods `PageMetaClass.get_tags`, `Client.upvote_tag` and `Client.downvote_tag`
* New method `search_tags`
* New object `PartialTag`
* `tag` attributes are now `List[PartialTag]`
* Decreased ratelimit to 1/1sec, 40/5min

Removed Features
#################


v0.8.1
-------
Bug Fixes
##########
* Relaxed regex on `File.get_mirrors` to avoid failing in certain edge cases

New Features
#############
* Increased ratelimit to 1/2.5sec, 60/5min
* New objects :class:`Thread`, :class:`Message` and :class:`ThreadThumbnail`

New :class:`.Client` methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
For sending and manipulating messages:
* :func:`Client.get_threads`
* :func:`Client.parse_thread`
* :func:`Client.send_message`
* :func:`Client.reply_to_thread`
* :func:`Client.add_member_to_thread`
* :func:`Client.leave_thread`
* :func:`Client.mark_all_read`
* :func:`Client.clear_watched`

Removed Features
#################


v0.8.0
-------
Bug Fixes
##########
* Improved parsing stability accross the board
* Fixed :func:`Addon.save`
* Fixed large memory usage of saving addons
* 

New Features
#############
* Ratelimits implemented: 1 request every 5 seconds up to 30 every 5 minutes.
* New error :class:`AwaitingAuthorisation`
* Monolithic pages.py split into submodule
* `parse` renamed to `parse_page`
* Added :func:`parse_results` to allow parsing any result list regardless of native support (such as tags)
* New support for mirrors as with the class :class:`Mirror` and `mirror` keyword for :func:`Addon.save` and :func:`File.save`
* New :func:`Comment.is_stale` method to make it easier to detect if a comment can still be used
* Renamed `ResultList.page` to `ResultList.current_page`
* Renamed `ResultList.max_page` to `ResultList.total_pages`
* Added `ResultList.total_results` to make it easier to access the total number of results
* Updated enums and included script for future updates
* Added `get_watcher` method to several page objects


Removed Features
#################
* Remove :class:`Search`, fused together back with :class:`ResultList`
* Removed `feedparser` dependency, RSS feed methods now only retun the URL
* Removed under the hood `robobrowser` dependency
* Removed obsolete `Engine.get_addons` method
* Removed `page_type` parameter in :func:`parse_page`


v0.7
-----
Bug Fixes
###########
* Links in comment content are now properly displayed as links rather than simply the domain name
* Changed get_all_results to return either :class:`.ResultList` or :class:`.CommentList` to allow for comment flattening
* Replace <a> tags (non-embed ones) in comment content by simply the href value of the tag
* Fixed bug with getting more results from :class:`.ResultList` for blogs and reviews

New Features
##############
* Add __contains__ for :class:`.ResultList`, :class:`.CommentList` and :class:`.Search`
* All get_comments now have access to the show_deleted kwarg
* Added :class:`.Review` id attribute
* Added attribute for Agree and Disagree :class:`.Review` links
* Added helper methods for finding object within sequences (find and get)

New :class:`.Client` Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Added support for adding comments
* Added support for deleting comments
* Added support for undeleting comments
* Added support for editing comments
* Added support for adding reviews to pages
* Added support for deleting review from page

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
    