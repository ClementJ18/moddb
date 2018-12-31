.. currentmodule:: moddb

Filtering and Sorting
=======================
When searching for pages you can often refine those searches using filters
and sorting. Filtering is the act of purposfully restricting the results
returned to only those matching a certain number of criterias and sorting 
is displaying those results based on the ascending or descending value of 
a field. 

The documentation for filtering and sorting models is found within the
documentation of the models themslves. E.g. To find the documentation
for filtering and sorting a Mod page, look at the :class:`Mod` documentation.

Filtering accepts any number of the arguments listed under the Filtering
section of each model. Sorting accepts a single argument along with the 
value 'desc' or 'asc'. You cannot sort by multiple arguments.

For example let's say we want to search for a mod, but we're only interested
in the most popular fantasy mods. In that case we'd want to filter by `theme` and
sort by `visittotal` and `asc`. E.g

::

    import moddb
    search = moddb.search(
                #what we're searching for
                moddb.SearchCategory.mods, 

                #a filter (there can be multiple)
                theme=moddb.Theme.fantasy, 

                #the sort tuple, there can only be one
                sort=('visitsalltime', 'asc')
            )

Simple as that, and the list of returned search results will be only the results 
which are themed Fantasy and will be sorted by all time popularity from highest
to lowest. Each item that can be searched has its own documentation on filtering 
and sorting and if it doesn't then open an issue on the Github repository of the 
project.