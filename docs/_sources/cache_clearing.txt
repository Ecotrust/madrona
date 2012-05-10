
.. _cache_clearing:

Clearing Cache
==============

Oftentimes changes made to your project code are not immediately reflected in your application.  
When this happens, there are various cache clearing strategies you may want to employ.  
 

Clearing your browser cache
---------------------------

Predictably, when changes are made to javascript or css files, you will need to run ``install_media`` (to update the shared media folder) and refresh your browser (so that it loads the most recent js and css).  
If these actions do not cause your code changes to appear in your application, you will want to try clearing your browser cache.

For *Firefox* browsers, the shortcut key ctrl-shift-del will bring up the Clear History dialog box permitting you to clear your cache.

For *Chrome* users, this same shortcut key ctrl-shift-del will bring up the Clear Browsing Data dialog allowing you to empty your cache.  

For other browsers (*IE*, *Safari*, etc), there is a fairly comprehensive and up to date `wikihow site <http://www.wikihow.com/Clear-Your-Browser%27s-Cache>`_ that explains appropriate steps based on the browser (and version) you may be using.  

Clearing your Google Earth cache
--------------------------------

Sometimes code changes that result in updated KML will require some trial and error.  
At times, such changes will be reflected in your application through a simple browser refresh.  
At other times, these changes may require the clearing of your browser's cache.  
At still other times, it may help to `clear the cache on your Google Earth client <http://support.google.com/earth/bin/answer.py?hl=en&answer=20712>`_ application.  

Additional Strategies
---------------------

Additional cache clearing strategies include:
 * restarting your web server and refreshing your browser
 * running the management command ``clear_cache`` (clears the django cache)
 * closing the application tab in your browser, clearing the browser cache, and opening the application in a new tab
 * viewing the application in a different browser 
 * finally, causing a KML change to occur at run-time (such as dragging/dropping features among folders in My Shapes) may do the trick
