.. currentmodule:: moddb
.. _snippets-ref:

Examples and Snippets
=======================
Here are presented some up to date snippets of things that can be done with the library.

The Client
------------
Clients represents an independtly logged in user. This allows you to make certain requests more easily, they don't need to be logged in to the library's session but rather those independent sessions can be used to make requests. They can be used to make requests with the methods provided by Client but can also be used to overwrite the module wide session to make any requests with any user. Firt, a simple example of using client:: 

    import moddb

    client = moddb.Client("Username", "Password")
    
    #standard request, we're just gonna get the update that have been posted.
    updates = client.get_updates()
    #list of special thumbnails representing the updates this user has
    cookie = client.get_freeman_cookie()

If you already have a valid `freeman` cookie, you can initialize a client directly with it::

    import moddb

    client = moddb.Client(freeman_cookie="...")
    updates = client.get_updates()

A simple little example, users have updates which happen when pages upload new articles, files and media. These are based on what pages users follow. But let's say we want to make one of the more general requests provided by the library without overwriting permanently the module session:: 

    import moddb

    #first we wanna loging as some base user
    moddb.login("RootUser", "RootPassword")
    #let's say root user has access to a lot of stuff, but when a user tries to use the system to check
    #something else we only give them partial access like this
    #create a client instance
    client = moddb.Client("RegularUser", "RegularPassword")

    #now we want to get something using that user's account, like their profile
    with client:
        member = moddb.parse_page("https://www.moddb.com/members/regularuser")

    #now we can see this profile from the persepctive of RegularUser.

The same cookie-based initialization works with :class:`TwoFactorAuthClient` as well::

    import moddb

    client = moddb.TwoFactorAuthClient(freeman_cookie="...")
    assert client.login() is True

You can also export the current session's cookie and re-use it later::

    import moddb

    moddb.login("Username", "Password")
    cookie = moddb.get_freeman_cookie()

    client = moddb.Client(freeman_cookie=cookie)
