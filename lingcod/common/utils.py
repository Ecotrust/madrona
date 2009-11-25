from django.contrib.gis.geos import Point
from math import pi, sin, tan, sqrt, pow
from django.conf import settings


def KmlWrap( string ):
    return '<?xml version="1.0" encoding="UTF-8"?> <kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">' + string + '</kml>'
    
    
def LookAtKml( geometry ):
    lookAtParams = ComputeLookAt( geometry )
    return '<LookAt><latitude>%f</latitude><longitude>%f</longitude><range>%f</range><tilt>%f</tilt><heading>%f</heading><altitudeMode>clampToGround</altitudeMode></LookAt>' % (lookAtParams['latitude'], lookAtParams['longitude'], lookAtParams['range'], lookAtParams['tilt'], lookAtParams['heading'] )

def LargestPolyFromMulti(geom): 
    """ takes a polygon or a multipolygon geometry and returns only the largest polygon geometry"""
    if geom.num_geom > 1:
        largest_area = 0.0
        for g in geom: # find the largest polygon in the multi polygon 
            if g.area > largest_area:
                largest_geom = g
                largest_area = g.area
    else:
        largest_geom = geom
    return largest_geom  
   
def ComputeLookAt( geometry ):

    lookAtParams = {}

    DEGREES = pi / 180.0
    EARTH_RADIUS = 6378137.0

    trans_geom = geometry.clone()
    trans_geom.transform(settings.GEOMETRY_DB_SRID) # assuming this is an equal area projection measure in meters

    w = trans_geom.extent[0]
    s = trans_geom.extent[1]
    e = trans_geom.extent[2]
    n = trans_geom.extent[3]
    
    center_lon = trans_geom.centroid.y
    center_lat = trans_geom.centroid.x
    
    lngSpan = (Point(w, center_lat)).distance(Point(e, center_lat)) 
    latSpan = (Point(center_lon, n)).distance(Point(center_lon, s))
    
    aspectRatio = 1.0

    PAD_FACTOR = 1.5 # add 50% to the computed range for padding
    
    aspectUse = max( aspectRatio, min((lngSpan / latSpan),1.0))
    alpha = (45.0 / (aspectUse + 0.4) - 2.0) * DEGREES # computed experimentally;
  
    # create LookAt using distance formula
    if lngSpan > latSpan:
        # polygon is wide
        beta = min(DEGREES * 90.0, alpha + lngSpan / 2.0 / EARTH_RADIUS)
    else:
        # polygon is taller
        beta = min(DEGREES * 90.0, alpha + latSpan / 2.0 / EARTH_RADIUS)
  
    lookAtParams['range'] = PAD_FACTOR * EARTH_RADIUS * (sin(beta) *
        sqrt(1.0 / pow(tan(alpha),2.0) + 1.0) - 1.0)
        
    trans_geom.transform(4326)
    
    lookAtParams['latitude'] = trans_geom.centroid.y
    lookAtParams['longitude'] = trans_geom.centroid.x
    lookAtParams['tilt'] = 0
    lookAtParams['heading'] = 0

    return lookAtParams
    
def get_class(path):
    from django.utils import importlib
    module,dot,klass = path.rpartition('.')
    m = importlib.import_module(module)
    return m.__getattribute__(klass)
    
def get_mpa_class():
    try:
        return get_class(settings.MPA_CLASS)
    except:
        raise Exception("Problem importing MPA class. Is MPA_CLASS defined correctly in your settings?")

def get_array_class():
    try:
        return get_class(settings.ARRAY_CLASS)
    except:
        raise Exception("Problem importing Array class. Is ARRAY_CLASS defined correctly in your settings?")

def get_mpa_form():
    try:
        return get_class(settings.MPA_FORM)
    except:
        raise Exception("Problem importing MPA form. Is MPA_FORM defined correctly in your settings?")
        
def get_array_form():
    try:
        return get_class(settings.ARRAY_FORM)
    except:
        raise Exception("Problem importing Array form. Is ARRAY_FORM defined correctly in your settings?")
    
def kml_errors(kmlstring):
    import feedvalidator
    from feedvalidator import compatibility
    events = feedvalidator.validateString(kmlstring, firstOccurrenceOnly=1)['loggedEvents'] 

    # Three levels of compatibility
    # "A" is most basic level
    # "AA" mimics online validator
    # "AAA" is experimental; these rules WILL change or disappear in future versions
    filterFunc = getattr(compatibility, "AA")
    events = filterFunc(events)

    # there are a few annoyances with feedvalidator; specifically it doesn't recognize 
    # KML ExtendedData element 
    # or our custom 'mm' namespance 
    # or our custom atom link relation
    # so we ignore all related events
    events = [x for x in events if not (
                (isinstance(x,feedvalidator.logging.UndefinedElement) and x.params['element']==u'ExtendedData') or
                (isinstance(x,feedvalidator.logging.UnregisteredAtomLinkRel) and x.params['value']==u'marinemap.update_form') or
                (isinstance(x,feedvalidator.logging.UnknownNamespace) and x.params['namespace']==u'http://marinemap.org')
                )]

    from feedvalidator.formatter.text_plain import Formatter
    output = Formatter(events)

    if output:
        errors = []
        for i in range(len(output)):
            errors.append( (events[i],events[i].params,output[i],kmlstring.splitlines()[events[i].params['backupline']]) )
        return errors
    else:
        return None
