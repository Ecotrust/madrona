.. _geojson:

GeoJSON output
====================================

Madrona provides `GeoJSON <http://www.geojson.org/>`_ output for by default. As expected, these are exposed through the REST API using an ``alternate`` generic link relation::

    /features/generic-links/links/geojson/{{instance.uid}}/

Nested vs Flat
--------------

Unfortunately the GeoJSON spec `does not allow FeatureCollection to be nested <http://www.geojson.org/geojson-spec.html#feature-collection-objects>`_ within other FeatureCollections as Madrona does. Given this nested feature structure::

         folder1
          |- mpa1
          |- folder2
              | - mpa2

You have two strategies for GeoJSON representation:

1. ``flat``: (Default) Flatten the geojson output and loose information about the heirarchical structure::

     FeatureCollection 
      |- mpa1
      |- mpa2

2. ``nest_feature_set``: The collection is represented as an empty geometry with a special ``feature_set`` property - a list of UIDs of the contained features. This is within the GeoJSON spec but fetching those contained features requires a client with knowledge of this convention::

     FeatureCollection 
      |- mpa1
      |- folder2 (with a `feature_set` list of uids and null geom)

You can specify the geojson strategy with a URL parameter like so::

    /features/generic-links/links/geojson/{{instance.uid}}/?strategy=nest_feature_set

Specifying the spatial reference system
----------------------------------------
By default, the GeoJSON geometries will be in the coordinate system of your database (defined by your ``GEOMETRY_DB_SRID`` setting).
You can set a different default by using the ``GEOJSON_SRID`` setting::

    GEOJSON_SRID = 3357  # default to web mercator

If you need a different coordinate system at runtime, you can specify an ``srid`` parameter on the URL::

    /features/generic-links/links/geojson/{{instance.uid}}/?srid=4326


Custom GeoJSON output
----------------------
To override the default geojson representation of a feature, you can specify a geojson method on your feature class 
which returns string containing a geojson feature (without a trailing comma)::
 
      { 
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [102.0, 0.5]},
        "properties": {"prop0": "value0"}
      }

.. important:: Your geojson method *must* take an ``srid`` argument and transform the geometry accordingly. 

In order to construct the geojson, there are several utility functions available. The example below show 
how you could add an additional property to the geojson feature::

    import json
    from madrona.common.jsonutils import get_properties_json, get_feature_json 

    class AOI(PolygonFeature):
        ...

        def geojson(self, srid):
            props = get_properties_json(self)
            props['absolute_url'] = self.get_absolute_url()
            json_geom = self.geometry_final.transform(srid, clone=True).json
            return get_feature_json(json_geom, json.dumps(props))


Geometry field
--------------
Unless you provide a custom geojson method on your feature class, the GeoJSON view will look for a geometry_final attribute.
If it doesn't exist for whatever reason, the GeoJSON geometry will be null. You can fake a geometry_final field 
by mirroring with a property::

        @property
        def geometry_final(self):
            return self.my_custom_geometry_field

But most likely you'll want to create a custom GeoJSON property.


Properties
----------
The GeoJSON feature properties are serialized directly from the feature instance. Not all fields are included though; 
Madrona strips out the following::

    unwanted_properties = [
        'geometry_final', 
        'geometry_orig', 
        'content_type', 
        'object_id', 
    ]

... and adds a ``uid`` property. This behavior can be overridden with a custom geojson method.  


Downloading
------------
The default behavior is to handle as a download (i.e. prompt the user to save the json file and give it a reasonable filename). This is done
through an HTTP ``Content-Disposition: attachment; filename={{instance_uid}}.geojson`` header. 
The default behavior can be controlled through a setting::

    GEOJSON_DOWNLOAD = True  # Default
    GEOJSON_DOWNLOAD = False  # don't treat like a downloadable attachment

Additionally, you can override the setting at runtime by adding an ``attach`` or ``noattach`` parameter to the URL::

    /features/generic-links/links/geojson/{{instance.uid}}/?attach
    /features/generic-links/links/geojson/{{instance.uid}}/?noattach



Turning off GeoJSON 
-------------------
You can specify an Option on your feature class to turn off geojson export::

    class AOI(PolygonFeature):
        ...
        class Options:
            export_geojson = False

