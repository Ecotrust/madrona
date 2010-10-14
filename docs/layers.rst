.. _layers:

Data Layers
===========

Adding Public Datasets
**********************
Public datasets used by MarineMap are managed using a single KML file. This
file uses ``NetworkLinks`` to refer to other datasets that can be hosted
anywhere else on the web.

creating a new layers list
--------------------------
Create a kml file using Google Earth that references other kml files on the 
web via `NetworkLinks <http://code.google.com/apis/kml/documentation/kml_tut.html#network_links>`_. 
An example of such a file can be found under 
``lingcode/layers/fixtures/public_layers.kml``. Once you have a kml file ready
go into the admin tool and choose **Public layer lists**. From there you can 
add a new layer. The most important thing to note here is be sure your first 
uploaded layer is set as *active*!

updating the layers list
------------------------
Once an initial layer list is loaded into the tool, the basic workflow to make 
changes is as follows.

#. download existing kml
#. open in google and make changes
#. save locally
#. use the admin site to create a new :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` with that kml file
#. mark the new :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` as active
    
This makes it easy to roll back to a previous version of the layer list as
needed.

Adding Private Datasets
***********************

Private datasets allow you to create and add additional layers with access control. You can choose to keep the layers entirely private or share them with select user groups.

Once you have the kml or kmz file created, go into the admin tool and choose **Private layer lists**. You can add as many layers as you wish but make sure you choose your username from the dropdown menu! This should be done automatically but is terribly difficult to implement for some reason; we are stuck manually assigning it. Also make sure you give it an appropriate name and a priority number. Finally, select one or more groups if you wish to share the layer with other user groups (if not, just leave it blank and it will be your own personal data layer).

In order to enable sharing within a group, you must grant the group the following permission::

    layers | private layer list | Can share private layers

To add the private layers to your marinemap site,add the following to your layerConfig block in the map template:: 

    lingcod.addLayer('{% url private-data-layers session_key=session_key %}');            

This will show up as a kml file with network links to all private layers accessible to the user (owned by them and shared with them via user groups).

For admin types: If you're installing a new system, you need to make sure that :class:`PrivateLayerList <lingcod.layers.models.PrivateLayerList>` is set configured for use with the sharing app. The easiest way to do this is to run the `manage.py layers_sharing` command.

Adding Private SuperOverlays
****************************

Overview
--------
SuperOverlays are multi-file KML heirarchies for displaying things like tiled rasters (created using the gdal2tiles utility for example). The key distinctions between a normal private dataset and a private superoverlay is that a) superoverlays must exist on disk (cant be uploaded via admin) and b) they allow authorized users to access *any* file in or below the directory of the base kml file. 

For example, consider this directory structure::
    
   - rockfish
     - doc.kml
     - something.txt
     - level1
       - doc.kml

If you create a PrivateLayerList with the kml set to `rockfish/doc.kml` you can access the base kml itself using the normal URL (assume pk=1, session_key=0)::
    
    http://localhost:8000/layers/overlay/1/0/

Or any path relative to this URL to access files in or below that directory::

    http://localhost:8000/layers/overlay/1/0/something.txt
    http://localhost:8000/layers/overlay/1/0/level1/doc.kml

The appended paths are sanitized according to the algorithm in django.views.static which ensures that only file at or below the base directory can be accessed. *If a user has access to the base kml, they also have access to every file at or below that directory level!* This has important security implications and it's highly recomended that you put each superoverlay in its own folder as a result. 

Setting up a superoverlay
-------------------------
1. Create a directory for superoverlays and set `settings.SUPEROVERLAY_ROOT`
#. Create the superoverlay. Must use relative paths and have a doc.kml which will serve as the base kml file. 
#. Transfer the superoverlay data directory to SUPEROVERLAY_ROOT
#. Set up layers sharing : `manage.py layers_sharing`
#. For each group that wishes to share superoveralys, they need this permission added::

    layers | private super overlay | Can share private super overlays

#. Using the Admin interface, add the private super overlay. The doc.kml file should appear in the dropdown
#. The superoverlay will now be included in the private data layers list (assuming this is added to the map):: 

    lingcod.addLayer('{% url private-data-layers session_key=session_key %}');            
   
#. Alternatively, you can access the layer directly through a reverse url lookup like so::

    {% url layers-superoverlay-private pk=1 session_key=session_key %}            

Legends
*******

Metadata
********

Temporal Data
*************

Tours
*****

Tools for Creating KML
**********************

Sources for Existing KML
************************
