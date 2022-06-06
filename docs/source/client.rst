.. currentmodule:: moddb.enums

Authenticating 
===============
The client object allows you to manipulate a user object that is logged in. Each client object represents a logged in user on which you can do a set of operations and requests. This gives you more interactivity with the website beyond simply getting random page. You can track, untrack pages and get the updates to those pages.

The client also supports __enter__ and __exit__ as means to temporarily replace the module's session with the client's. See snippets for an example.

Client
---------
.. autoclass:: moddb.client.Client
    :members:
    :inherited-members:

Update
-----------
.. autoclass:: moddb.client.Update
    :members:
    :inherited-members:
    

Request
-----------
.. autoclass:: moddb.client.Request
    :members:
    :inherited-members:
    