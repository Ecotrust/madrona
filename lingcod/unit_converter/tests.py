"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.conf import settings
from django.contrib.gis import geos
from lingcod.unit_converter.models import *
from django.contrib.gis.measure import *

# Number of digits to round results to for comparison
NUM_DIGITS = 4

def create_test_geometries():
    geoms = {}
    poly = geos.fromstr('POLYGON ((-370109.1943174076732248 256715.2728654230013490, -376985.4612110010348260 257023.5105245867744088, -376389.0298118293867446 266349.4951122021302581, -369815.3686999985366128 265947.4629999864846468, -370941.4576000009546988 259130.8280999893322587, -370109.1943174076732248 256715.2728654230013490))')
    line = geos.fromstr('LINESTRING (-370109.1943174076732248 256715.2728654230013490, -376985.4612110010348260 257023.5105245867744088)')
    mpoly = geos.MultiPolygon(poly, geos.fromstr('POLYGON ((-340404.9563809176324867 383194.1489779399707913, -341376.1892856784397736 378422.7254901370033622, -346118.1728583426447585 378627.0628479672595859, -345907.4695642645237967 383431.2573733469471335, -340404.9563809176324867 383194.1489779399707913))'))
    mline = geos.MultiLineString(line, geos.fromstr('LINESTRING (-340404.9563809176324867 383194.1489779399707913, -341376.1892856784397736 378422.7254901370033622, -346118.1728583426447585 378627.0628479672595859)'))
    gc_polys = geos.GeometryCollection(poly, mpoly)
    gc_lines = geos.GeometryCollection(line, mline)
    gc_everything = geos.GeometryCollection(poly,line,mpoly,mline)
    geoms = {
        'poly': poly,
        'line': line,
        'mpoly': mpoly,
        'mline': mline,
        'gc_polys': gc_polys,
        'gc_lines': gc_lines,
        'gc_everything': gc_everything,
    }
    for geom in geoms.values():
        geom.srid = 3310
    return geoms
    
def meter_measurements(geoms):
    rdict = {}
    for k,v in geoms.iteritems():
        if k.find('line') > -1:
            rdict[k] = v.length
        else:
            rdict[k] = v.area
    return rdict
    
def meter_dict_convert(mdict,unit):
    con_dict = {}
    for k,v in mdict.iteritems():
        if k.find('line') > -1:
            con_dict[k] = D(m=v).__getattr__(unit)
        else:
            con_dict[k] = A(sq_m=v).__getattr__('sq_' + unit)
    return con_dict

class SettingsTest(TestCase):
    def test_settings(self):
        """
        Make sure that the necessary settings exist and are appropriate.
        """
        dlu = settings.DISPLAY_LENGTH_UNITS
        dau = settings.DISPLAY_AREA_UNITS
        gds = settings.GEOMETRY_DB_SRID
        self.failIf(None in [dlu,dau,gds])
        
        for unit in [dlu,dau]:
            self.failIf( unit not in D.UNITS.keys() + A.UNITS.keys() )
            
class AppendedMethodsTest(TestCase):
    def test_appended_methods(self):
        geoms = create_test_geometries()
        m_dict = meter_measurements(geoms)
        mi_dict = meter_dict_convert(m_dict,'mi')
        ft_dict = meter_dict_convert(m_dict,'ft')
        km_dict = meter_dict_convert(m_dict,'km')
        display_dict = meter_dict_convert(m_dict,settings.DISPLAY_LENGTH_UNITS)
        units_dict = {
            'm': m_dict,
            'mi': mi_dict,
            'ft': ft_dict,
            'km': km_dict,
            settings.DISPLAY_LENGTH_UNITS: display_dict,
        }
        add_conversion_methods_to_GEOSGeometry()
        
        for unit, result_dict in units_dict.iteritems():
            for key, geom in geoms.iteritems():
                fail_str = "unit = %s, key = %s, dict value = %f" % (unit,key,result_dict[key])
                if key.find('line') > -1:
                    att_name = 'length_' + unit
                else:
                    att_name = 'area_sq_' + unit
                fail_str += ', appended method value = %f' % getattr(geom,att_name)
                self.assertAlmostEqual(result_dict[key],getattr(geom,att_name),NUM_DIGITS,fail_str)
            
class OtherMethodsTest(TestCase):
    def test_other_methods(self):
        unit = settings.DISPLAY_LENGTH_UNITS
        geoms = create_test_geometries()
        m_dict = meter_measurements(geoms)
        result_dict = meter_dict_convert(m_dict,unit)
        
        for key, geom in geoms.iteritems():
            fail_str = "unit = %s, key = %s, dict value = %f" % (unit,key,result_dict[key])
            if key.find('line') > -1:
                att_name = 'length_' + unit
            else:
                att_name = 'area_sq_' + unit
            fail_str += ', appended method value = %f' % getattr(geom,att_name)
            self.assertAlmostEqual(result_dict[key],getattr(geom,att_name),NUM_DIGITS,fail_str)



