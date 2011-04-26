.. _kmlapp:

`lingcod.kmlapp`: KML Representation of Features and Collections
================================================================

.. note::
    Why call it `kmlapp` instead of simply `kml`? That namespace conflicts with the python bindings for libkml. 

.. note::
    Certain aspects of KML require absolute URLs and thus require configuring 
    the site domain with the `Django Sites framework <http://docs.djangoproject.com/en/dev/ref/contrib/sites/>`_. 
    You can do this by setting the domain name of your server
    through the admin tool (e.g. http://localhost:8000/admin/sites/site/1/).

Simple Styling Parameters
***************************
The classification of MPAs is based on their "MPA Designation" (e.g. State Marine Park, State Marine Conservation Area, etc.). Each MPA Designation has an associated fill color and border color that can be configured through the admin interface. 

The colors are given in 8 digit HEX codes. These differ significantly from the typical 6 digit codes where each 2-digit chunk represents red, green, blue. Instead, the 8 digit code uses a "transparency, blue, green, red" order.  

This classification and styling system is also used by the static map tool. 

KML Templates
**********************
The layout of the KML document is configured using the django templating system. You can override some or all of these templates by placing your customized versions in a TEMPLATE_DIR that is loaded before the kmlapp/templates directory (See `Loading Templates <http://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates>`_ in the django docs).

  * base.kml configures the overall top-level structure of the KML document. You won't need to chance much in this file other than the docname. 
  * style.kml configures the style definition for each MPA designation including the symbology and the html to be displayed in the popup balloon. 
  * placemark.kml organizes the MPAs into folders by Array, sets the extended data elements of the MPA and outputs the placemark geometries.
  * placemark_links.kml is similar to placemark.kml but, instead of creating a folder containing all MPAs in each array, it uses network links to the KML representations of each array (allowing for faster loading, caching, etc)

Service Options
**********************
There are three primary ways to access KML representations of MPAs:

  * All MPAs belonging to a user. (e.g. http://example.com/kml/username/user_mpa.kml)
  * All MPAs belonging to a given array. (e.g. http://example.com/kml/1/array.kml)
  * Individual MPAs. (e.g. http://example.com/kml/1/mpa.kml)

All three can be retrieved as a zipped KMZ file by accessing the service with .kmz instead of .kml

There is one additional way to access user MPAs which uses Network Links for each array to increase performance (rather than putting all MPA placemarks into a single file). This service can be accessed as both a kml or kmz. The URL for this service would be something like http://example.com/kml/username/user_mpa_links.kml . 
