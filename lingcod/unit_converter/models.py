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
    """Get the unit from the srid definition."""
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
    return area_unit_code_from_srid_unit( units_from_srid(srid) )

def distance_unit_code_from_srid(srid):
    return distance_unit_code_from_srid_unit( units_from_srid(srid) )
    
def units_list():
    units = []
    for srid in srid_list():
        unit = units_from_srid(srid)
        if not unit in units:
            units.append(unit)
    return units
    
def units_count_dict():
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
    eval_str = "Distance(%s=%f)" % (distance_unit_code_from_srid(self.srid),self.length)
    return eval(eval_str)
        
@property
def area_object(self):
    eval_str = "Area(%s=%f)" % (area_unit_code_from_srid(self.srid),self.length)
    return eval(eval_str)

def add_dist_meth(cls,unit):
    @property
    def new_dist_meth(self):
        return self.distance_object.__getattr__(unit)
    name = "length_%s" % unit
    setattr(cls,name,new_dist_meth)

def add_area_meth(cls,unit):
    @property
    def new_area_meth(self):
        return self.area_object.__getattr__(unit)
    name = "area_%s" % unit
    setattr(cls,name,new_area_meth)

def add_conversion_methods_to_GEOSGeometry():
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
    if geom.srid:
        srid = geom.srid
    else:
        srid = settings.GEOMETRY_DB_SRID
    eval_str = "Distance(%s=%f).%s" % (distance_unit_code_from_srid(srid),geom.length,settings.DISPLAY_LENGTH_UNITS)
    return eval(eval_str)
    
def geometry_area_in_display_units(geom):
    if geom.srid:
        srid = geom.srid
    else:
        srid = settings.GEOMETRY_DB_SRID
    eval_str = "Area(%s=%f).%s" % (area_unit_code_from_srid(srid),geom.area,settings.DISPLAY_AREA_UNITS)
    return eval(eval_str)
    
def length_in_display_units(geom_or_num):
    from django.contrib.gis.geos import GEOSGeometry as GG
    if issubclass(geom_or_num.__class__,GG): # This means it is a geometry
        return geometry_length_in_display_units(geom_or_num)
    else:
        return convert_float_to_length_display_units(geom_or_num)
        
def area_in_display_units(geom_or_num):
    from django.contrib.gis.geos import GEOSGeometry as GG
    if issubclass(geom_or_num.__class__,GG): # This means it is a geometry
        return geometry_area_in_display_units(geom_or_num)
    else:
        return convert_float_to_area_display_units(geom_or_num)
    