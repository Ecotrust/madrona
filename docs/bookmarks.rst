`lingcod.bookmarks`: Bookmark the map state
===========================================

Introduction
------------
Bookmarks save the google earth camera settings and the public layer list state and serialize it to a shortened URL that can be used to restore the map state.
There are two mechanisms by which bookmarks can be used: The bookmark tool in the Tools panel (required in all lingcod-based apps) and bookmark features which show up in the My Shapes kmltree (optional).
Internally, these are handled by the same mechanism but the "Bookmarks as a Feature" functionality can be turned off via a setting. 

Bookmarks as a Feature
----------------------
Will show up in Create New > Bookmark and can be shared, copied, etc just like any other feature. This can be enabled by setting ``BOOKMARK_FEATURE = True``. Defaults to False.

Bookmarks Tool
--------------
This will show up as a button in the tools panel. Clicking the button will POST the data to the server and save the Bookmark object under an anonymous user account (username is set by ``BOOKMARK_ANON_USERNAME``). 
These can be created by any user including unauthenticated users. The bookmark URL will appear directly below the button and can be copy-and-pasted as needed. 
You can set a limit on the number of bookmarks by IP address using the ``BOOKMARK_ANON_LIMIT`` settings; A tuple providing the number of requests and the time delta. 
For example, the default setting is ``(100, timedelta(minutes=30))`` which translates to 100 bookmarks per IP every 30 minutes. 

Serialization
-------------
The bookmarks will try to recreate your map state as closely as possible. The camera settings and public layer lists are preserved fully but keep in mind
that any private layers and features that you see may not necessarily be available to other user and are not included in the bookmark state. 

