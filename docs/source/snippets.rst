.. moddb documentation master file, created by
   sphinx-quickstart on Fri Dec 28 17:23:26 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. currentmodule:: moddb
.. _snippets-ref:


Examples and Snippets
=======================
Here are presented some up to date snippets of things that can be done with the library.

Getting every page of a search
--------------------------------
Results returned from a page are paginated into 30 result pages and getting all of them can be pretty annoying. Of course, your first reflex should be to try and adjust the search settings to get a more precie return and hence hopefully return less results. However, if you are ever in the need to get **all** the results for a given search you can do something like:: 

    import moddb

    #lets say we want to see all the mods produced for the "Rise of the Witch King" game, just a couple pages but a good enough
    #example. Since we know the id, we can just go ahead and make a simple moddb.Object to get it.

    fake_game = moddb.Object(id=10009)
    search = moddb.search(moddb.SearchCategory.mods, game=fake_game)
    results = search.results

    while not search.page == search.page_max:
        search = search.next_page()
        results.extend(search.results)
        print(search.page)

    # what if we want a very specific order? no problem, the Search object takes care of it all, we just have to tell it
    # what we want at the start and it'll assure persistence in sorting.
    search = moddb.search(moddb.SearchCategory.mods, game=fake_game, sort=('visitstotal', 'desc'))
    results = search.results

    while not search.page == search.page_max:
        search = search.next_page()
        results.extend(search.results)
        print(search.page)

Reusing filters
----------------
Filters are a cool thing, they allow you to limit the amount of result you return to be more tailored to what you're actually looking for. But what if you want to do multiple searches with the same filters? You could save them as a dict which you then unpack into the search function and keep saved somewhere sure, but why bother, the Search object already stores the filters so just piggy off that and you'll be fine.::

    import moddb
    #I swear I don't have a LOTR bias. Also, this is a simple example, assume we have dozens of filters.
    fake_game = moddb.Object(id=10009)
    search = moddb.search(moddb.SearchCategory.mods, game=fake_game)
    #so now we have a set of filters, now let's say we wanna fine tune the search a bit more, let's says we also only want
    #the mods that have been released in the last year
    search = moddb.search(moddb.SearchCategory.mods, timeframe=moddb.TimeFrame.year, **search.filters)
