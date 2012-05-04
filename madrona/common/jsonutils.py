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

