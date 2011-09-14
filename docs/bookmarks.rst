
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

Public Data Layer KML Guidelines
--------------------------------
The layer state only captures the **differences** between your current tree and the default state of the original KML document. Both expanded/collapsed properties (for folders and netlinks) and visible/hidden properties (for features) are captured. KMLTree uses the folder and feature names to track the items so changing the public layer KML can have some repercussions for existing bookmarks. As such, there are several “best practices” for constructing public KML docs

.. _bookmarks:
#. Avoid renaming folders or features unless absolutely necessary. 
#. Avoid restructuring folder hierarchies unless absolutely necessary. 
#. Keep all the folders collapsed and features turned off in the initial doc. If, for some reason, you need to have a feature turned on by default, it should remain so for all subsequent revisions.
#. Adding new layers is fine as long as their default state is OFF.
#. Changing out datasets is fine as long as they keep the same name. E.g. if you add a new revised “Nesting Sites” folder, keep the name “Nesting Sites” consistent; don’t call it “Nesting Sites version 2”. And if you change the location of the "Site #12" don't rename it. 
#. Keep the names unique within each folder level.
#. Avoid deleting content from the KML unless necessary. Someone may have used that data in a bookmark. 

The worst that can happen if you ignore these rules is that existing bookmarks may not restore the layer tree state in the expected way.

For example, if a user created a bookmark with “Nautical Charts” turned on and you rename to “Nautical Charts, new version”, the existing bookmark will not find the original layer and the new nautical chart will not be visible. The camera angle will still be bookmarked but the changes to the KML will make that bookmark’s layer state invalid.  Still, the bookmark will not be “broken” and it will not crash; it will just cause unexpected changes in behavior.

