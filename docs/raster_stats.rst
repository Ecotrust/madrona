.. _raster_stats:

Raster Statistics App
=======================
The `lingcod.raster_stats` app allows you to analyze raster datasets based on a polygon geometry. For example, for a given polygon, you may want to know the average elevation or the maximum temperature, etc. Essentially this performs a vector-on-raster intersection. 

The app uses an optional caching mechanism so that any geometry/raster combination only needs to be run once. 

The raster_stats app provides a model to register raster datasets, a utility function to quickly calculate stats programatically and a webservice which returns the statistics in json format.

Installation
------------
The raster_stats app relies on the `starspan` executable. This C++ app must be installed from src and requires GDAL and GEOS header files::

    wget http://projects.atlas.ca.gov/frs/download.php/667/starspan-1.2.03.tar.gz
    tar -xzvf starspan-1.2.03.tar.gz
    cd starspan-1.2.03
    ./configure
    make
    sudo make install

If you get errors similar to::

    src/csv/Csv.h:52: error: ‘stdout’ was not declared in this scope

it means that you are probably compiling with a newer version of GCC (eg GCC 4.4 which ships with Ubuntu 10.4) and does not include some standard libraries by default. This means that you need to explicitly include them (eg add `#include <cstdio>` to the affected files). We also have a patched version available at http://marinemap.org/downloads/starspan-1.2.04.tar.gz

Settings
--------
optionally set the `STARSPAN_BIN` setting to point to your starspan executable and the `RASTER_DIR` setting for the filepath to the directory containing your raster files.

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
The app provides a urls.py file; just point your main URLCONF file to it::

    (r'^zonal/', include('lingcod.raster_stats.urls')),

You can get a json list of the rasters at this url::

	http://localhost/zonal/

And you can append the raster name and supply a `geom_txt` parameter (either wkt or json) which returns the rasters stats as json::

	http://localhost/zonal/sst/?geom_txt=POLYGON ((-122.735420504497029 37.238868044757552,-122.516579972608298 37.245550198403009,-122.50822728055148 37.043415050627928,-122.730408889262932 37.046756127450656,-122.735420504497029 37.238868044757552))

	[
         {"pk": 764, "model": "raster_stats.zonalstatscache", 
          "fields": {"raster": 23, "min": 0.0, "max": 1.5440739999999999, "geom_hash": "-8107990604081680573", 
                     "nulls": 0.0, "median": 0.28777199999999997, "mode": 0.0, "stdev": 0.44484400000000002, 
                     "date_modified": "2010-06-23 19:00:30", "avg": 0.40776400000000002, "pixels": 531.0}
         }
        ]
