.. _staticmap:

`lingcod.staticmap`: Static Map Data Layers
===========================================

Default Datasets
**********************
MarineMap ships with several example datasets. These default datasets are in ESRI Shapefile format and stored in <MEDIA_ROOT>/staticmap/data/.

#. Land Mask (Based on the "Global Self-consistent, Hierarchical, High-resolution Shoreline" dataset and clipped to southern california region - full dataset available from `EVS Islands <http://www.evs-islands.com/2007/11/data-global-land-mask-using-vectors.html>`_.
#. World ports dataset. (`The Geography of Transport Systems <http://www.people.hofstra.edu/geotrans/eng/media.html>`_)

In addition there are django fixtures (ie initial data to populate the database) 

#. study regions
#. marine protected areas

These models contain polygon fields and are represented as postgis geometry fields in the database. Since mapnik can also render data from a postgis data source, these are added to the default map.

Adding Datasets
**********************
The staticmap application uses `Mapnik <http://mapnik.org>`_ to render map images from spatial data. Specifically, we use the `mapnik XML files <http://trac.mapnik.org/wiki/XMLConfigReference>`_ to configure the spatial data sources and their styling. If you are unfamiliar with Mapnik, we suggest going over the the `XML Configuration Tutorial <http://trac.mapnik.org/wiki/XMLGettingStarted>`_ first.  

The default mapnik XML config file (<MEDIA_ROOT>/staticmap/socal.xml) is a good starting point. You will need to add two main XML elements in order to set up any additional data for the staticmap

Layer
------
This element defines the path/connection to the data source, the spatial reference system of the input data and the name of the style to use::

  <Layer name="world" srs="+proj=latlong +datum=WGS84">
    <StyleName>My Style</StyleName>
    <Datasource>
      <Parameter name="type">shape</Parameter>
      <Parameter name="file">/path/to/your/world_borders</Parameter>
    </Datasource>
  </Layer>

Style
------
This element defines "rules" which determine the colors, symbology, classification and filtering of the data. In the simplest case, you will simply define a single style for all features in the layer::

  <Style name="My Style">
    <Rule>
      <PolygonSymbolizer>
        <CssParameter name="fill">#f2eff9</CssParameter>
      </PolygonSymbolizer>
      <LineSymbolizer>
        <CssParameter name="stroke">rgb(50%,50%,50%)</CssParameter>
        <CssParameter name="stroke-width">0.1</CssParameter>
      </LineSymbolizer>
    </Rule>
  </Style>


As an alternative to editing xml text files, you can try `Quantumnik <http://bitbucket.org/springmeyer/quantumnik/wiki/Home>`_ which allows you to use Quantum GIS to style the layers in a familiar GIS graphic interface and export the map as a mapnik XML.

Note on spatial reference systems
----------------------------------
The spatial reference system (SRS) of each layer should be explicitly defined using a `proj4 string <http://trac.osgeo.org/proj/wiki/GenParms>`_. Its important to note that this is the SRS of the original data source - it is not necessarily the SRS of the output map. If the SRS defined in the Map element differs from the Layer SRS, mapnik will reproject each Layer to the common SRS of the Map.

Adding maps to the staticmap application
*****************************************
If you create a new mapnik xml map, you'll need to register it with your django project. First, login to the django admin site and navigate to Home › Staticmap › Map configs › Add map config. Here you will define the short n name of your new map, the initial map dimensions and the path to the xml file. 

To access your new map, hit http://your.domain.com/staticmap/yourmapname

Accessing maps by URL
*********************
The staticmap can be accessed by url template tags::

    <img align="top" src="{% url staticmap-show 'default' %}">

The staticmap view also takes several parameters to configure the map

  * `uids` : a comma-seperated list of feature uids. If the feature uid is a feature collection, staticmap will attempt to draw all features contained in that collection.
  
  * `width` and `height` : Dimensions of the output image (in pixels)

  * `bbox` : a comma-seperated list of four floating point values representing the geographic extent of the output map (ie minx,miny,maxx,maxy)

  * `autozoom` : set to 'True' if you need the map to automatically set the geographic extent according to the selected features.

  * `show_extent` : set to 'True' if you need to show a box indicating the extent of selected features. Useful for overview maps.


You could incorporate these into a django template as follows::

    <img align="top" src="{% url staticmap-show 'default' %}?uids={{ feature.uid }}&amp;width=154&amp;height=200&amp;show_extent=True">

