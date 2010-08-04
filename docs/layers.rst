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
