
Project Architecture
====================

Madrona allows you to focus on the actual problem your project is trying to solve (rather than technical minutia) and keeps your application modular and flexible. Here's how:

.. image:: madrona_outline.png

Features 
--------------------
The majority of a madrona-based tool revolves around building models of the ``Features`` you want to include in the tool.
Features are the driver of your application behavior; they are the entities important to your decision/planning process.

    * Created and managed by users
    * Have a spatial representation
    * Can have non-spatial attributes and properties
    * Relate to other Features
    * Can contain other features (i.e. a collection of features)
    * Have defined behaviors (views and methods)
    * Can have complex reporting and analysis
    * Typically represented as a KML object
    * Are defined with Django models

Features are registered with Madrona and most of the functionality is determined on the fly, eliminating the need to write boilerplate code. Specifically, the feature models automatically drive:

    * Django urls, views and forms
    * A fully-featured REST API
    * Client-side javascript libraries

The REST API 
-----------------------
The method by which users will interact with ``Features`` via HTTP.

Besides the standard `CRUD` operations: 
    * Create
    * Read
    * Update 
    * Delete

The Default REST API provides for advanced views:
    * KML and other spatial data formats
    * Reports
    * Static maps
    * Sharing / Collaboration
    * Copying
    * Importing
    * Exporting
    * Moving

Most importantly, Madrona provides the ability to quickly extend API to expose additional fuctionality pertaining to your features. 

Finally, the entire REST API is described by a ``workspace`` document (JSON format) which defines the available feature classes and the URLS to interact with them.

The javascript/HTML client
---------------------------
Madrona ships with a full-fledged js/html client. Based on jQuery and the Google Earth plugin, this interface reads the ``workspace`` document from the REST API and configures itself accordingly. 

.. image:: 3dclient.png

The 3D map client interface consists of three components:

    * The ``KMLEditor`` provides a menu for interacting with the REST API. This includes creating new features and accessing contextualy-appropriate actions that the user can apply to selected features. 
    * The ``KMLTree`` component provides a tree view of the KML representation of your features.
    * The map component, provided by the ``Google Earth plugin``, provides a 3D interative map to interact with the features spatially. 

.. note:: 2D mapping clients are supported but there is currently no out-of-the-box client interface for 2D. 


Software stack
--------------

On the Server
    * Python WSGI
    * GeoDjango
    * PostGIS
    * GDAL/OGR
    * External analytics (e.g. GRASS, Marxan, ArcGIS)

On the Client
    * JQuery
    * Google Earth API
