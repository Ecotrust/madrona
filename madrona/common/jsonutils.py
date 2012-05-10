"""
GeoJSON helper functions
"""
from django.core import serializers
import json

def get_properties_json(i):
    json_orig = serializers.serialize('json', [i,])
    # use_natural_keys=True is not reliable; can fail w/ content_type error:
    #     'NoneType' object has no attribute 'natural_key'
    obj = json.loads(json_orig)
    props = obj[0]['fields']
    unwanted_properties = [
        'geometry_final', 
        'geometry_orig', 
        'content_type', 
        'object_id', 
    ]
    for uwp in unwanted_properties:
        try:
            props.pop(uwp)
        except:
            pass
    # Add uid
    props['uid'] = i.uid
    return props

def get_feature_json(geom_json, prop_json):
    return """{
        "type": "Feature",
        "geometry": %s, 
        "properties": %s
    }""" % (geom_json, prop_json)

def srid_to_urn(srid):
    """
    Take a postgis srid and make it into a OGC CRS URN
    As suggested by http://www.geojson.org/geojson-spec.html#named-crs
    This is pretty dumb right now and just assumes EPSG as the authority
    except for 4326 which uses:
      4326 -> urn:ogc:def:crs:OGC:1.3:CRS84
    """
    if int(srid) == 4326:
        return "urn:ogc:def:crs:OGC:1.3:CRS84"
    
    return "urn:ogc:def:crs:EPSG::%d" % srid

def srid_to_proj(srid):
    """
    Take a postgis srid and return the proj4 string
    Useful for custom projections with no authority
    """
    from django.contrib.gis.gdal import SpatialReference
    srs = SpatialReference(srid) 
    return srs.proj.strip()

