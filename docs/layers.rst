.. _layers:

`lingcod.layers`: KML Data Layers
=================================
This document outlines how KML base data layers are handled in MarineMap. 

There are two categories of KML layers to consider:

* **User Uploaded KMLs** are controlled by the user through the web interface. These act as ``Features`` and can be shared, managed through the MarineMap application, put into folders, etc. These will show up in the "My Shapes" and "Shared with Me" Tabs.
  
* **Admin Managed KMLs** are managed by the site administrators on the server or through the admin site. They cannot be managed through the MarineMap application front-end, only viewed. Data can be uploaded directly onto the server with sftp. They aren't treated like features, they don't use the sharing API or have any of the built in functionality of ``Features``. They'll only show up in the data layers panel or wherever you choose to put them in your site template.

  Of these, there are two sub-types of admin-managed KMLs:

  * **Private KMLs** can be single KMLs or superoverlay trees which are only available to select groups. 

  * **Public Layer Lists** is a single KML file that is used to represent all publically-available data layers.
  

Adding Public KML Datasets
***************************
Public datasets, accessible to all users, are managed using a single KML file. This
file uses ``NetworkLinks`` to refer to other datasets that can be hosted
anywhere else on the web.

creating a new layers list
--------------------------
Create a kml file using Google Earth that references other kml files on the 
web via `NetworkLinks <http://code.google.com/apis/kml/documentation/kml_tut.html#network_links>`_. 
An example of such a file can be found under 
``lingcod/layers/fixtures/public_layers.kml``. Once you have a kml file ready
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

best practices for creating/updating public KMLs
------------------------------------------------
With the advent of bookmarking functionality, updating public KMLs can have some repercussions for the existing bookmarks. 
Please :ref:`follow the guidelines <bookmarks>` to avoid disrupting any user's bookmarks. 

Adding Restricted-Access KML Datasets
*************************************

Private KMLs allow you to create and add additional layers with access control. You can choose to keep the layers entirely private or share them with select user groups.


Adding Restricted-Access KML SuperOverlays
-------------------------------------------
SuperOverlays are multi-file KML heirarchies for displaying things like tiled rasters (created using the gdal2tiles utility for example). The key distinctions between a normal private dataset and a private superoverlay is that a) superoverlays must exist on disk (cant be uploaded via admin) and b) they allow authorized users to access *any* file in or below the directory of the base kml file. 

For example, consider this directory structure::
    
   - rockfish
     - doc.kml
     - something.txt
     - level1
       - doc.kml

If you create a PrivateKML with the kml set to `rockfish/doc.kml` you can access the base kml itself using the normal URL (assume pk=1, session_key=0)::
    
    http://localhost:8000/layers/overlay/1/0/

Or any path relative to this URL to access files in or below that directory::

    http://localhost:8000/layers/overlay/1/0/something.txt
    http://localhost:8000/layers/overlay/1/0/level1/doc.kml

The appended paths are sanitized according to the algorithm in django.views.static which ensures that only file at or below the base directory can be accessed. *If a user has access to the base kml, they also have access to every file at or below that directory level!* This has important security implications and it's highly recomended that you put each superoverlay in its own folder as a result. 

Setting up private KMLs
-----------------------
1. Create a directory for private KMLS and set `settings.PRIVATE_KML_ROOT`
#. Transfer the data to PRIVATE_KML_ROOT. For best results, it's highly recomended that each dataset get it's own subdirectory, especially if you are dealing with superoverlays.

#. Using the Admin interface, add the privatekml. The .kml/.kmz files should appear in the dropdown
#. Alternatively, you can run a management command to auto-create private kml entries and share them with a group. This is based on the exisiting contents of PRIVATE_KML_ROOT. You'll probaby want to tweak the PrivateKml entries via admin later but this provides a decent starting point.::

    python manage.py create_privatekml GroupName

#. The private will now be included in the private data layers list (assuming this is added to the map):: 

    lingcod.addLayer('{% url layers_privatekml_list session_key=session_key %}');            
   
#. Alternatively, you can access each PrivateKml directly through a reverse url lookup like so::

    {% url layers-privatekml pk=1 session_key=session_key %}            

