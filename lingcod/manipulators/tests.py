"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.gis.geos import *
from lingcod.studyregion.models import StudyRegion
from django.core import serializers 
from manipulators import *      

urlpatterns = patterns('',
    # Example:
    (r'/manipulators/', include('lingcod.manipulators.urls')),
)


class ManipulatorsTest(TestCase):
    def setUp(self):
        '''
            Build geometries for the following test cases:
            code0_poly    clip to study region / clip to shape
            code1_poly    clip to graticule
            code2_poly    outside study region / outside shape
            code3_poly    invalid geometry 
            other case    missing kwargs
        '''
        
        #NOTE:  lat/lon (4326) coords are created with Point(lon, lat) (iow not (lat, lon))
        self.code0_poly = Polygon(LinearRing([Point(-1,-1), Point(1,-1), Point(1,-3), Point(-1,-3), Point(-1,-1)]))
        self.code1_poly = fromstr('POLYGON ((-1 1, 1 1, 1 -1, -1 -1, -1 1))') # area = 4
        self.code2_poly = fromstr('POLYGON ((3 3, 4 3, 4 4, 3 4, 3 3))') # area = 1
        self.code3_poly = fromstr('POLYGON ((3 3, 4 3, 3 4, 4 4, 3 3))') # area = 0
        
        self.study_region = fromstr('POLYGON ((-2 2, 2 2, 2 -2, -2 -2, -2 2))')
        
        self.client = Client()
        
    def tearDown(self):
        self.code0_poly = None
        self.code1_poly = None
        self.code2_poly = None
        self.code3_poly = None
        
        self.study_region = None
   
        self.client = None
        
    def testManipulators(self):
        #call individual test methods from here
        self.manipulatorViewTest()
        self.clipToShapeTest()
        self.clipToStudyRegionTest()
        self.clipToGraticuleTest()
        self.multipleManipulatorTest()
        
    def manipulatorViewTest(self):
        '''
            test views.generic_manipulator_view
        '''
        trans_geom = StudyRegion.objects.current().geometry
        trans_geom.transform(settings.GEOMETRY_CLIENT_SRID)
        
        w = trans_geom.extent[0]
        s = trans_geom.extent[1]
        e = trans_geom.extent[2]
        n = trans_geom.extent[3]
        
        center_lat = trans_geom.centroid.y 
        center_lon = trans_geom.centroid.x
                
        target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))

        # test study region manipulator
        response = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape':target_shape.wkt, })
        self.assertEquals(response.status_code, 200)
        
        # test graticules
        response = self.client.post('/manipulators/ClipToGraticule/', {'target_shape':target_shape.wkt, "north":"40", "south":"30", "east":"-118", "west":"-119"})
        self.assertEquals(response.status_code, 200)
        import pdb
        pdb.set_trace()
        # test non-trivial multi manipulator case
        response = self.client.post('/manipulators/ClipToStudyRegion,ClipToGraticule/', {'target_shape':target_shape.wkt, "north":"40", "south":"30", "east":"-118", "west":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
        # test reversed order of manipulators
        response = self.client.post('/manipulators/ClipToGraticule,ClipToStudyRegion/', {'target_shape':target_shape.wkt, "north":"40", "south":"30", "east":"-118", "west":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
        # test clip to study region and to shape 
        response = self.client.post('/manipulators/ClipToStudyRegion,ClipToShape/', {'target_shape': self.code1_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response.status_code, 200)
        
        # test clip to shape and to study region
        response = self.client.post('/manipulators/ClipToShape,ClipToStudyRegion/', {'target_shape': self.code1_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response.status_code, 200)
        
    def clipToShapeTest(self):
        '''
            Tests the following:
                clipped to shape
                intersection produced an empty geometry
                one or the other geometry is not valid
                missing kwargs
        '''
        
        #clipped to shape
        response0 = self.client.post('/manipulators/ClipToShape/', {'target_shape': self.code0_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response0.status_code, 200)
        shape_clipper = ClipToShapeManipulator(target_shape=self.code0_poly.wkt, clip_against=self.study_region.wkt)
        result = shape_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1) 
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #empty intersection
        response2 = self.client.post('/manipulators/ClipToShape/', {'target_shape': self.code2_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response2.status_code, 200)
        shape_clipper = ClipToShapeManipulator(target_shape=self.code2_poly.wkt, clip_against=self.study_region.wkt)
        result = shape_clipper.manipulate()
        self.assertEquals(result["clipped_shape"].area, 0)
        self.assertAlmostEquals(result["original_shape"].area, 1, places=1)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #invalid geometr(y/ies)
        response3 = self.client.post('/manipulators/ClipToShape/', {'target_shape': self.code3_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response3.status_code, 200)
        try:
            graticule_clipper = ClipToShapeManipulator(target_shape=self.code3_poly)
        except InvalidGeometryException:
            pass
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToShape/', {})
        self.assertEquals(response6.status_code, 200)
        try:
            ClipToShapeManipulator()
        except TypeError:
            pass
        
    def clipToStudyRegionTest(self):
        '''
            Tests the following:
                clipped to study region
                outside study region
                geometry not valid
                missing kwargs
        '''

        #clipped to study region 
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code0_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response0.status_code, 200)
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=self.code0_poly.wkt, study_region=self.study_region.wkt)
        result = studyregion_clipper.manipulate()
        #thought there might be a problem with places needing to be equal to 1 here, but
        #I tested it independently and it returns the same 1.9552852... value as ClipToStudyRegionManipulator
        #just part of transforming and intersecting I reckon
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1) 
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)

        #outside of study region
        response2 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code2_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response2.status_code, 200)
        try:
            graticule_clipper = ClipToStudyRegionManipulator(target_shape=self.code2_poly)
        except HaltManipulations:
            pass

        #geometry not valid
        response3 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code3_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response3.status_code, 200)
        try:
            graticule_clipper = ClipToStudyRegionManipulator(target_shape=self.code3_poly)
        except InvalidGeometryException:
            pass
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToStudyRegion/', {})
        self.assertEquals(response6.status_code, 200)
        try:
            ClipToStudyRegionManipulator()
        except TypeError:
            pass
    
        
    def clipToGraticuleTest(self):
        '''
            Tests the following:
                clipped to graticule
                clipping produced an empty geometry
                geometry not valid
                failed to create graticule clipped geometry
                missing kwargs
        '''
        #clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'east': .5, 'west': -.5})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, east=.5, west=-.5)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #another clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'north': .5, 'south': -.5})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, north=.5, south=-.5)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #another clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'west': 0})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, west=0)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #test with bad graticule values
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'west': 3})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, west=3)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 0, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #test with no graticule values
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 4, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        self.assertEquals(result["clipped_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        self.assertEquals(result["original_shape"].srid, settings.GEOMETRY_CLIENT_SRID)
        
        #test with bad geometry
        response3 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code3_poly.wkt})
        self.assertEquals(response3.status_code, 200)
        try:
            graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code3_poly)
        except InvalidGeometryException:
            pass
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToGraticule/', {'east': 3, 'west': -3})
        self.assertEquals(response6.status_code, 200)
        try:
            graticule_clipper = ClipToGraticuleManipulator(east=3, west=-3)
        except TypeError:
            pass
            
    #Multiple Manipulators testing 
    def multipleManipulatorTest(self):
        '''
            Tests the following:
                clip to study region and clip to estuaries manipulations
                clip to study region and clip to graticules manipulations
                
        '''
        #clip to study region and to shape test
        response1 = self.client.post('/manipulators/ClipToStudyRegion,ClipToShape/', {'target_shape': self.code1_poly.wkt, 'clip_against': self.study_region.wkt})
        self.assertEquals(response1.status_code, 200)
        #clip to study region and clip to graticules test
        response1 = self.client.post('/manipulators/ClipToStudyRegion,ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'east': .5})
        self.assertEquals(response1.status_code, 200)
    