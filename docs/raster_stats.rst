.. _raster_stats:

Raster Statistics App
=======================
The `lingcod.raster_stats` app allows you to analyze raster datasets based on a polygon geometry. For example, for a given polygon, you may want to know the average elevation or the maximum temperature, etc. Essentially this performs a vector-on-raster intersection. 

The app uses an optional caching mechanism so that any geometry/raster combination only needs to be run once. 

The raster_stats app provides a model to register raster datasets, a utility function to quickly calculate stats programatically and a webservice which returns the statistics in json format.

Installation
------------
The raster_stats app relies on the `starspan` executable. This C++ app must be installed from src and it's a pain. The end. 

http://projects.atlas.ca.gov/frs/download.php/667/starspan-1.2.03.tar.gz

Settings
--------
optionally set the `STARSPAN_BIN` setting to point to your starspan executable.

Then just add to your installed apps::

    INSTALLED_APPS += ( 'lingcod.raster_stats' )

Adding a Raster
---------------
Simple as it gets. Type can be continuous(eg elevation surface) or categorical(eg land use categories)::
    
    from lingcod.raster_stats.models import RasterDataset
    rast = RasterDataset.objects.create(name="test_impact",filepath='/tmp/data/impact.tif',type='continuous')  

Running zonal stats
-------------------
Use the utility function which will first check the cache. If nothing is in the cache, the full starspan analysis is run. Otherwise the cache hit is returned::

    from lingcod.raster_stats.models import zonal_stats
    stats = zonal_stats(geos_polygon_geom, rast)
    stats.from_cache # False
    
    stats = zonal_stats(geos_polygon_geom, rast)
    stats.from_cache # True
    stats.min 
    stats.max
    stats.median
    stats.mode
    stats.nulls
    stats.pixels
    stats.avg
    stats.stdev

Using the web service
---------------------
TODO
