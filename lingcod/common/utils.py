import os
from django.contrib.gis.geos import Point, LinearRing, fromstr
from math import pi, sin, tan, sqrt, pow
from django.conf import settings
from django.db import connection
import zipfile

#from django.db import transaction

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
   
def angle(pnt1,pnt2,pnt3):
    """
    Return the angle in radians between line(pnt2,pnt1) and line(pnt2,pnt3)
    """
    cursor = connection.cursor()
    if pnt1.srid:
        query = "SELECT abs(ST_Azimuth(ST_PointFromText(\'%s\',%i), ST_PointFromText(\'%s\',%i) ) - ST_Azimuth(ST_PointFromText(\'%s\',%i), ST_PointFromText(\'%s\',%i)) )" % (pnt2.wkt,pnt2.srid,pnt1.wkt,pnt1.srid,pnt2.wkt,pnt2.srid,pnt3.wkt,pnt3.srid)
    else:
        query = "SELECT abs(ST_Azimuth(ST_PointFromText(\'%s\'), ST_PointFromText(\'%s\') ) - ST_Azimuth(ST_PointFromText(\'%s\'), ST_PointFromText(\'%s\')) )" % (pnt2.wkt,pnt1.wkt,pnt2.wkt,pnt3.wkt)
    #print query
    cursor.execute(query)
    row = cursor.fetchone()
    return row[0]
    
def angle_degrees(pnt1,pnt2,pnt3):
    """
    Return the angle in degrees between line(pnt2,pnt1) and line(pnt2,pnt3)
    """
    rads = angle(pnt1,pnt2,pnt3)
    return rads * (180/pi)

def spike_ring_indecies(line_ring,threshold=0.01):
    """
    Returns a list of point indexes if ring contains spikes (angles of less than threshold degrees).
    Otherwise, an empty list.
    """
    radian_thresh = threshold * (pi/180)
    spike_indecies = []
    for i,pnt in enumerate(line_ring.coords):
        if(i==0 and line_ring.num_points > 3): # The first point  ...which also equals the last point
            p1_coords = line_ring.coords[len(line_ring.coords) - 2]
        elif(i==line_ring.num_points-1): # The first and last point are the same in a line ring so we're done
            break
        else:
            p1_coords = line_ring.coords[i - 1]
            
        # set up the points for the angle test.
        p1_str = 'POINT (%f %f), %i' % (p1_coords[0], p1_coords[1], settings.GEOMETRY_DB_SRID)
        p1 = fromstr(p1_str)
        p2_str = 'POINT (%f %f), %i' % (pnt[0],pnt[1],settings.GEOMETRY_DB_SRID)
        p2 = fromstr(p2_str)
        p3_coords = line_ring.coords[i + 1]
        p3_str = 'POINT (%f %f), %i' % (p3_coords[0], p3_coords[1], settings.GEOMETRY_DB_SRID)
        p3 = fromstr(p3_str)
        if( angle(p1,p2,p3) <= radian_thresh ):
            spike_indecies.append(i)
    
    return spike_indecies

def remove_spikes(poly,threshold=0.01):
    """
    Looks for spikes (angles < threshold degrees) in the polygons exterior ring.  If there are spikes,
    they will be removed and a polygon (without spikes) will be returned.  If no spikes are found, method
    will return original geometry.
    
    NOTE: This method does not examine or fix interior rings.  So far those haven't seemed to have been a problem.
    """
    line_ring = poly.exterior_ring
    spike_indecies = spike_ring_indecies(line_ring,threshold=threshold)
    if( spike_indecies ):
        for i,org_index in enumerate(spike_indecies):
            if(org_index==0): # special case, must remove first and last point, and add end point that overlaps new first point
                # get the list of points
                pnts = list(line_ring.coords)
                # remove the first point
                pnts.remove(pnts[0])
                # remove the last point
                pnts.remove(pnts[-1])
                # append a copy of the new first point (old second point) onto the end so it makes a closed ring
                pnts.append(pnts[0])
                # replace the old line ring
                line_ring = LinearRing(pnts)
            else:
                line_ring.remove(line_ring.coords[org_index])
        poly.exterior_ring = line_ring
    return poly
    
def clean_geometry(geom):
    """Send a geometry to the cleanGeometry stored procedure and get the cleaned geom back."""
    cursor = connection.cursor()
    query = "select cleangeometry(st_geomfromewkt(\'%s\')) as geometry" % geom.ewkt
    cursor.execute(query)
    row = cursor.fetchone()
    newgeom = fromstr(row[0])
    # sometimes, clean returns a multipolygon
    geometry = LargestPolyFromMulti(newgeom)

    if not geometry.valid or (geometry.geom_type != 'Point' and geometry.num_coords < 2):
        raise Exception("I can't clean this geometry. Dirty, filthy geometry. This geometry should be ashamed.")
    else:
        return geometry

# transforms the geometry to the given srid, checks it's validity and 
# cleans it if necessary, transforms it back into the original srid and
# cleans again if needed before returning 
# Note, it does not scrub the geometry before transforming, so if needed
# call check_validity(geo, geo.srid) first.
def ensure_clean(geo, srid):
    old_srid = geo.srid
    if geo.srid is not srid:
        geo.transform(srid)
    geo = clean_geometry(geo)
    if not geo.valid:
        raise Exception("ensure_clean could not produce a valid geometry.")
    if geo.srid is not old_srid:
        geo.transform(old_srid)
        geo = clean_geometry(geo)
        if not geo.valid:
            raise Exception("ensure_clean could not produce a valid geometry.")
    return geo
   
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

def get_spatial_class_names():
    """
    Create a list of spatial types which show up in kmltree
    TODO: Currently just assumes that MPA and Arrays are the only kmltree-able models
    """
    mk = get_mpa_class()
    ak = get_array_class()
    return [mk._meta.object_name.lower(), ak._meta.object_name.lower()]
    
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
    # or space-delimited Icon states
    # so we ignore all related events
    events = [x for x in events if not (
                (isinstance(x,feedvalidator.logging.UndefinedElement) and x.params['element']==u'ExtendedData') or
                (isinstance(x,feedvalidator.logging.UnregisteredAtomLinkRel) and x.params['value']==u'marinemap.update_form') or
                (isinstance(x,feedvalidator.logging.UnregisteredAtomLinkRel) and x.params['value']==u'marinemap.create_form') or
                (isinstance(x,feedvalidator.logging.UnknownNamespace) and x.params['namespace']==u'http://marinemap.org') or
                (isinstance(x,feedvalidator.logging.UnknownNamespace) and x.params['namespace']==u'http://www.google.com/kml/ext/2.2') or
                (isinstance(x,feedvalidator.logging.InvalidItemIconState) and x.params['element']==u'state' and ' ' in x.params['value']) 
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

def hex8_to_rgba(hex8):
    """
    Takes an 8 digit hex color string (used by Google Earth) and converts it to RGBA colorspace
    * 8-digit hex codes use AABBGGRR (R - red, G - green, B - blue, A - alpha transparency)
    """
    hex8 = str(hex8.replace('#',''))
    if len(hex8) != 8:
        raise Exception("Hex8 value must be exactly 8 digits")
    hex_values = [hex8[i:i+2:1] for i in xrange(0, len(hex8), 2)]
    rgba_values = [int(x,16) for x in hex_values]
    rgba_values.reverse()
    return rgba_values
    
from django.utils.importlib import import_module

def load_session(request, session_key):
    log = get_logger()
    if session_key and session_key != '0':
        engine = import_module(settings.SESSION_ENGINE)
        request.session = engine.SessionStore(session_key)

def valid_browser(ua):
    """
    Returns boolean depending on whether we support their browser
    based on their HTTP_USER_AGENT

    Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7
    Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-us) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10
    """
    supported_browsers = [
            ('Firefox', 3, 5, 'Mac'),
            ('Safari', 3, 1, 'Mac'),
            ('Chrome', 6, 0, 'Mac'),
            ('Firefox', 3, 5, 'Windows'),
            ('Chrome', 1, 0, 'Windows'),
            ('IE', 8, 0, 'Windows'),
    ]

    from lingcod.common import uaparser

    bp = uaparser.browser_platform(ua)

    for sb in supported_browsers:
        if bp.family == sb[0] and \
           ((bp.v1 == sb[1] and bp.v2 >= sb[2]) or bp.v1 > sb[1]) and \
           bp.platform == sb[3]:
               return True

    return False

class KMZUtil:
    """
    Recursively adds a directory to a zipfile
    modified from http://stackoverflow.com/questions/458436/adding-folders-to-a-zip-file-using-python
    
    from lingcod.common.utils import ZipUtil
    zu = ZipUtil()
    filename = 'TEMP.zip'
    directory = 'kmldir' # containing doc.kml, etc
    zu.toZip(directory, filename)
    """
    def toZip(self, file, filename):
        zip_file = zipfile.ZipFile(filename, 'w')
        if os.path.isfile(file):
            zip_file.write(file)
        else:
            self.addFolderToZip(zip_file, file)
        zip_file.close()

    def addFolderToZip(self, zip_file, folder): 
        if not folder or folder == '':
            folder_path = '.'
        else:
            folder_path = folder

        # first add doc.kml - IMPORTANT that it be the first file added!
        doc = os.path.join(folder,'doc.kml')
        if os.path.exists(doc):
            #print 'File added: ' + str(doc)
            zip_file.write(doc)

        for file in os.listdir(folder_path):
            full_path = os.path.join(folder, file)
            if os.path.isfile(full_path) and not full_path.endswith("doc.kml"):
                #print 'File added: ' + str(full_path)
                zip_file.write(full_path)
            elif os.path.isdir(full_path):
                #print 'Entering folder: ' + str(full_path)
                self.addFolderToZip(zip_file, full_path)

import logging
import inspect
import tempfile
def get_logger(caller_name=None):
    try:
        logfile = settings.LOG_FILE
    except:
        logfile = os.path.join(tempfile.gettempdir(),'marinemap_log.txt')
        print "WARNING: settings.LOG_FILE not specified; using %s instead" % logfile

    try:
        # Use overall debug settings to determine loglevel
        if settings.DEBUG:
            level = logging.DEBUG
        else:
            level = logging.WARNING 
    except:
        level = logging.DEBUG
    
    logging.basicConfig(level=level,
                format='%(asctime)s %(name)s %(levelname)s %(message)s',
                filename=logfile)

    if not caller_name:
        caller = inspect.currentframe().f_back
        caller_name = caller.f_globals['__name__']

    logger = logging.getLogger(caller_name)
    return logger


def isCCW(ring):
    """
    Determines if a LinearRing is oriented counter-clockwise or not
    """
    area = 0.0
    for i in range(0,len(ring)-1):
        p1 = ring[i]
        p2 = ring[i+1]
        area += (p1[1] * p2[0]) - (p1[0] * p2[1])

    if area > 0:
        return False
    else:
        return True


from django.contrib.gis.geos import Polygon
def forceRHR(polygon):
    """
    reverses rings so that polygon follows the Right-hand rule
    exterior ring = clockwise
    interior rings = counter-clockwise
    """
    assert polygon.geom_type == 'Polygon'
    assert not polygon.empty
    exterior = True
    rings = []
    for ring in polygon:
        assert ring.ring # Must be a linear ring at this point
        if exterior:
            if isCCW(ring):
                ring.reverse()
            exterior = False
        else:
            if not isCCW(ring):
                ring.reverse()
        rings.append(ring)
    poly = Polygon(*rings)
    return poly

def forceLHR(polygon):
    """
    reverses rings so that geometry complies with the LEFT-hand rule
    Google Earth KML requires this oddity
    exterior ring = counter-clockwise
    interior rings = clockwise
    """
    assert polygon.geom_type == 'Polygon'
    assert not polygon.empty
    exterior = True
    rings = []
    for ring in polygon:
        assert ring.ring # Must be a linear ring at this point
        if exterior:
            if not isCCW(ring):
                ring.reverse()
            exterior = False
        else:
            if isCCW(ring):
                ring.reverse()
        rings.append(ring)
    poly = Polygon(*rings)
    return poly

def asKml(geom):
    """
    Performs three critical functions for creating suitable KML geometries:
     - simplifies the geoms (lines, polygons only)
     - forces left-hand rule orientation
     - extrudes the shape to 3 dimensions (polygon only)
    """
    if geom.geom_type in ['Polygon','LineString']:
        geom = geom.simplify(settings.KML_SIMPLIFY_TOLERANCE_DEGREES)

    if geom.geom_type == 'Polygon':
        geom = forceLHR(geom)
        
    kml = geom.kml

    if geom.geom_type == 'Polygon':
        kml = kml.replace('<Polygon>', '<Polygon><altitudeMode>absolute</altitudeMode><extrude>1</extrude>')
        # The GEOSGeometry.kml() method always adds a z dim = 0
        kml = kml.replace(',0', ',%s' % settings.KML_EXTRUDE_HEIGHT)

    return kml

