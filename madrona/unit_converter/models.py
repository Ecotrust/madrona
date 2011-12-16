from django.db import models, connection
from django.conf import settings
from osgeo import osr
from django.contrib.gis.measure import *
from django.contrib.gis.geos.polygon import Polygon

def srid_list():
    """Return a list of numberic srids by looking in the spatial_ref_sys table of the db."""
    cursor = connection.cursor()
    query = "select auth_srid from spatial_ref_sys"
    cursor.execute(query)
    results = cursor.fetchall()
    return [ a[0] for a in results ]
    
def units_from_srid(srid):
    """Get the linear units name from the srid definition."""
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(srid)
    units = srs.GetLinearUnitsName()
    if units.lower() == 'meter' or units.lower() == 'metre':
        units = 'meter'
    return units
    
def area_unit_code_from_srid_unit(srid_unit):
    """Look at Area.LALIAS (a dictionary of lower case aliases found in srid definitions for units) and return the proper unit
    abbreviation used in the django.contrib.gis.measure.Area class."""
    return Area.LALIAS[srid_unit.lower()]
    
def distance_unit_code_from_srid_unit(srid_unit):
    """Look at Distance.LALIAS (a dictionary of lower case aliases found in srid definitions for units) and return the proper unit
    abbreviation used in the django.contrib.gis.measure.Distance class."""
    return Distance.LALIAS[srid_unit.lower()]
    
def area_unit_code_from_srid(srid):
    """Return the unit code used in django.contrib.gis.measure.Area to represent the units of the given srid.  For example srid
    3310 (California Albers) has a linear unit value of 'metre'.  django.contrib.gis.measure.Area uses 'sq_m' to represent square
    meters so that's what this method will return for srid 3310."""
    return area_unit_code_from_srid_unit( units_from_srid(srid) )

def distance_unit_code_from_srid(srid):
    """Return the unit code used in django.contrib.gis.measure.Distance to represent the units of the given srid.  For example srid
    3310 (California Albers) has a linear unit value of 'metre'.  django.contrib.gis.measure.Distance uses 'm' to represent 
    meters so that's what this method will return for srid 3310."""
    return distance_unit_code_from_srid_unit( units_from_srid(srid) )
    
def units_list():
    """Return a non repeating list of all the linear units from the spatial_ref_sys table."""
    units = []
    for srid in srid_list():
        unit = units_from_srid(srid)
        if not unit in units:
            units.append(unit)
    return units
    
def units_count_dict():
    """Return a dictionary with linear units as keys and a count of how many projections in the spatial_ref_sys table use 
    those units as values."""
    units = {}
    for srid in srid_list():
        unit = units_from_srid(srid)
        if not unit in units.keys():
            units.update({unit: 1})
        else:
            cnt = units[unit] + 1
            units.update({unit: cnt})
    return units

@property
def units(self):
    """Returns the name of the units, derived from the projection, for a given geometry."""
    if self.srid:
        return units_from_srid(self.srid)
    else:
        raise Exception("This geometry must have an srid if you want to know the units.")
        
@property
def distance_object(self):
    """Return the django.contrib.gis.measure.Distance object for a given geometry with origin units determined by 
    the geometry's srid.  This object can be evaluated by looking at the attribute named after the proper units.
    For instance if you want to see the distance in miles, call distance_object.mi"""
    eval_str = "Distance(%s=%f)" % (distance_unit_code_from_srid(self.srid),self.length)
    return eval(eval_str)
        
@property
def area_object(self):
    """Return the django.contrib.gis.measure.Area object for a given geometry with origin units determined by 
    the geometry's srid. This object can be evaluated by looking at the attribute named after the proper units.
    For instance if you want to see the area in square miles, call distance_object.sq_mi"""
    eval_str = "Area(%s=%f)" % (area_unit_code_from_srid(self.srid),self.area)
    return eval(eval_str)

def add_dist_meth(cls,unit):
    """Add a method to cls called length_UNIT (where UNIT is the value of unit) that will return the length in
    those units.  unit must be one of the values found in django.contrib.gis.measure.Distance.UNITS  Most 
    common will be mi, m, km, nm, ft"""
    @property
    def new_dist_meth(self):
        return self.distance_object.__getattr__(unit)
    name = "length_%s" % unit
    setattr(cls,name,new_dist_meth)

def add_area_meth(cls,unit):
    """Add a method to cls called area_UNIT (where UNIT is the value of unit) that will return the length in
    those units.  unit must be one of the values found in django.contrib.gis.measure.Area.UNITS  Most 
    common will be sq_mi, sq_m, sq_km, sq_nm, sq_ft"""
    @property
    def new_area_meth(self):
        return self.area_object.__getattr__(unit)
    name = "area_%s" % unit
    setattr(cls,name,new_area_meth)

def add_conversion_methods_to_GEOSGeometry():
    """Add a bunch of methods to the GEOSGeometry object.  After running this method once, all subsequent geos
    geometries will have methods to report out their length and area in any of the units listed in Area.UNITS or
    Distance.UNITS.  If you have a polygon called poly and want its length in mi, you can just call poly.length_mi.
    If you want the area in square centimeters, call poly.area_sq_cm.  Additionally, you can call poly.area_in_display_units
    or poly.length_in_display_units and get the measurments in the units specified in settings."""
    from django.contrib.gis.geos import GEOSGeometry as GG
    GG.units = units
    GG.distance_object = distance_object
    GG.area_object = area_object
    for unit in Distance.UNITS.keys():
        add_dist_meth(GG,unit)
    for unit in Area.UNITS.keys():
        add_area_meth(GG,unit)
    if settings.DISPLAY_LENGTH_UNITS:
        GG.length_units = settings.DISPLAY_LENGTH_UNITS
        l_meth_name = 'length_' + settings.DISPLAY_LENGTH_UNITS
        GG.length_in_display_units = getattr(GG,l_meth_name)
    if settings.DISPLAY_AREA_UNITS:
        GG.area_units = settings.DISPLAY_AREA_UNITS
        a_meth_name = 'area_' + settings.DISPLAY_AREA_UNITS
        GG.area_in_display_units = getattr(GG,a_meth_name)
        
        
##################################################
#  The following methods do not depend on the ones above.
#  They're generally much simpler and easier to use but
#  they're not as cool (and by cool I mean dorky).  
##################################################

def convert_float_to_length_display_units(float_value):
    """Given a float value, this method will convert from the units found in settings.GEOMETRY_DB_SRID
    to the units defined in settings.DISPLAY_LENGTH_UNITS."""
    eval_str = "Distance(%s=%f).%s" % (distance_unit_code_from_srid( settings.GEOMETRY_DB_SRID ), float_value, settings.DISPLAY_LENGTH_UNITS)
    return eval(eval_str)
    
def convert_float_to_area_display_units(float_value):
    """Given a float value, this method will convert from the units found in settings.GEOMETRY_DB_SRID
    to the units defined in settings.DISPLAY_AREA_UNITS."""
    eval_str = "Area(%s=%f).%s" % (area_unit_code_from_srid( settings.GEOMETRY_DB_SRID ), float_value, settings.DISPLAY_AREA_UNITS)
    return eval(eval_str)
    
def geometry_length_in_display_units(geom):
    """For a given geometry, return the geometry length in the units specified as settings.DISPLAY_LENGTH_UNITS. If the geometry has
    an srid, assume the origin units are the ones appropriate to that srid.  If there is no assigned srid, assume the srid is the one
    in settings.GEOMETRY_DB_SRID."""
    if geom.srid:
        srid = geom.srid
    else:
        srid = settings.GEOMETRY_DB_SRID
    eval_str = "Distance(%s=%f).%s" % (distance_unit_code_from_srid(srid),geom.length,settings.DISPLAY_LENGTH_UNITS)
    return eval(eval_str)
    
def geometry_area_in_display_units(geom):
    """For a given geometry, return the geometry area in the units specified as settings.DISPLAY_AREA_UNITS. If the geometry has
    an srid, assume the origin units are the ones appropriate to that srid.  If there is no assigned srid, assume the srid is the one
    in settings.GEOMETRY_DB_SRID."""
    if geom.srid:
        srid = geom.srid
    else:
        srid = settings.GEOMETRY_DB_SRID
    eval_str = "Area(%s=%f).%s" % (area_unit_code_from_srid(srid),geom.area,settings.DISPLAY_AREA_UNITS)
    return eval(eval_str)
    
def length_in_display_units(geom_or_num):
    """Take either a geometry or a numeric length value and convert to display units."""
    from django.contrib.gis.geos import GEOSGeometry as GG
    if issubclass(geom_or_num.__class__,GG): # This means it is a geometry
        return geometry_length_in_display_units(geom_or_num)
    else:
        return convert_float_to_length_display_units(geom_or_num)
        
def area_in_display_units(geom_or_num):
    """Take either a geometry or a numeric area value and convert to display units."""
    from django.contrib.gis.geos import GEOSGeometry as GG
    if issubclass(geom_or_num.__class__,GG): # This means it is a geometry
        return geometry_area_in_display_units(geom_or_num)
    else:
        return convert_float_to_area_display_units(geom_or_num)
    