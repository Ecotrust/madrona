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
