.. _loadshp:

`lingcod.loadshp`: Load Shapefile (loadshp) App
============================
The `lingcod.loadshp` app provides a mechanism to upload shapefiles, validate their contents and convert to KML. This can be used by the marinemap application to allow uploading shapefiles in lieu of digitizing a shape (useful in cases where a complex boundary may have already been developed outside of MarineMap).

The loadshp app borrows heavily from the django_shapes project but has been modified/extended to fit the needs of MarineMap.

Integration with MarineMap
--------------------------

In order to enable the loadshp functionality, add the following to your model Options class::

    class Options:
        ...
        geometry_input_methods = ['loadshp']

When the "Create New Shape" panel is displayed, this will be passed as a json variable which will trigger the display/activation of the appropriate html and javascript. 

Most of the UI code to integrate the shapefile loading functionality resides in the manipulators.js file. Only the views and forms are provided by `loadshp`.

.. note::

    The web service currently only provides the capability of loading a single polygon shapefile. Other geometry types and multi-feature shapefiles are not supported at this time. The service returns a somewhat bastardized format (KML wrapped in JSON wrapped in a <textarea>) in order to work around the limitations of the jQuery form plugin.


