
Custom Projections
==================

The EPSG database (installed with proj and postgis) has thousands of common reference systems.
However, sometimes your project will require a custom spatial reference system for which there is no corresponding SRID code.

You need to run a few steps immediately after you create your database:

#. Determine the proj4 definition of your spatial reference system. For example, we'll use custom Albers Equal Area defined as::

       +proj=aea +lat_1=37.25 +lat_2=40.25 +lat_0=36 +lon_0=-72 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs 

#. Make up a custom SRID; say `99996`. Add the proj4 definition to the bottom of ``/usr/local/share/proj/epsg`` (might be in another location)::

    # Marco Albers
    <99996> +proj=aea +lat_1=37.25 +lat_2=40.25 +lat_0=36 +lon_0=-72 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs <>


#. Set `GEOMETRY_DB_SRID = 99996` in settings.py BEFORE you run syncdb

#. then run the following command from django shell in order to add the projection to the spatial_ref_sys table::

    from django.contrib.gis.utils import add_postgis_srs
    add_postgis_srs(99996) 
