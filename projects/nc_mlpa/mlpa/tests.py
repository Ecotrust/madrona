"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from mlpa.models import *
from django.conf import settings
from django.conf.urls.defaults import *

from views import *
from django.contrib.gis.geos import *
from django.core import serializers

urlpatterns = patterns('',
    (r'/mlpa/', include('mlpa.urls')),
)

class MlpaValidateTest(TestCase):
    '''
        Commands used to run the following test (from the python shell command line):
            from mlpa.tests import *
            tester = MlpaValidateTest('testManipulators')
            tester.setUp()
            tester.testManipulators()
            tester.tearDown()
        
        Or the following to run as unit test:
            python manage.py test mlpa
            this calls setUp, testManipulators, and tearDown, in that order
    '''
    fixtures = ['example_data']

    def setUp(self):
        '''
            Build geometries for the following test cases:
            code0_poly  clips successfully
            code1_poly  overlaps with estuary, oceanic part chosen
            code2_poly  target geometry lies outside of geometry being clipped against
                            or in the case of Estuary clipping, no estuaries were found to clip against
            code3_poly  target geometry is not valid
            code4_poly  this code has the most meanings, each depending on context
                            in the case of Estuary clipping, it means the target was estuary only
            code5_poly  overlaps with estuary, estuary part chosen
            other case  one or more required kwargs not provided
        '''
        
        self.code0_poly = fromstr('SRID=4326;POLYGON ((-1 -1, 1 -1, 1 -3, -1 -3, -1 -1))') # area = 4
        self.code1_poly = fromstr('SRID=4326;POLYGON ((-1 1, 1 1, 1 -1, -1 -1, -1 1))') # area = 4
        self.code2_poly = fromstr('SRID=4326;POLYGON ((3 3, 4 3, 4 4, 3 4, 3 3))') # area = 1
        self.code3_poly = fromstr('SRID=4326;POLYGON ((3 3, 4 3, 3 4, 4 4, 3 3))') # area = 0
        self.code4_poly = fromstr('SRID=4326;POLYGON ((0 2, 1 0, 2 2, 0 2))') # area = 2
        self.code5_poly = fromstr('SRID=4326;POLYGON ((0 2, 2 2, 2 1, 0 1, 0 2))') # area = 2
        
        self.study_region = fromstr('SRID=4326;POLYGON ((-2 2, 2 2, 2 -2, -2 -2, -2 2))')
        
        self.est1 = fromstr('SRID=4326;POLYGON ((0 2, 1 0, 2 2, 0 2))') # same as code4_poly
        self.est2 = fromstr('SRID=4326;POLYGON ((0 2, -1 0, -2 2, 0 2))') # est1.area == est2.area == 2
        self.ests = MultiPolygon(self.est1, self.est2)
   
        self.client = Client()
        
    def tearDown(self):
    
        self.code0_poly = None
        self.code1_poly = None
        self.code2_poly = None
        self.code3_poly = None
        self.code4_poly = None
        self.code5_poly = None
        
        self.study_region = None
        
        self.est1 = None
        self.est2 = None
        self.ests = None
   
        self.client = None
        
    def testManipulators(self):   
        self.clipToGraticuleTest()
        self.clipToStudyRegionTest()
        self.clipToEstuariesTest()
        self.multipleManipulatorTest()
        self.clipToNCMLPATest()
        
        
    #Clip To Graticule testing (similar testing is already done in manipulators.tests)
    def clipToGraticuleTest(self):
        '''
            Tests the following:
                clip to graticule
        '''
        #clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': display_kml(self.code1_poly), 'west': .5, 'east': -.5})
        self.assertEquals(response1.status_code, 200)
        graticule_clipper = ClipToGraticuleManipulator(target_shape=display_kml(self.code1_poly), west=.5, east=-.5)
        result = graticule_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
    
    #Clip To Study Region testing (similar testing is already done in manipulators.tests)
    def clipToStudyRegionTest(self):
        '''
            Tests the following:
                clipped to study region
                outside study region
                geometry not valid
        '''
        #clip to study region
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': display_kml(self.code0_poly), 'study_region': self.study_region.wkt})
        self.assertEquals(response0.status_code, 200)
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=display_kml(self.code0_poly), study_region=self.study_region)
        result = studyregion_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        
        #outside study region
        response2 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': display_kml(self.code2_poly), 'study_region': self.study_region.wkt})
        self.assertEquals(response2.status_code, 200)
        try:
            graticule_clipper = ClipToStudyRegionManipulator(target_shape=display_kml(self.code2_poly))
        except HaltManipulations:
            pass
        
        #geometry not valid
        response3 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': display_kml(self.code3_poly), 'study_region': self.study_region.wkt})
        self.assertEquals(response3.status_code, 200)
        try:
            graticule_clipper = ClipToStudyRegionManipulator(target_shape=display_kml(self.code3_poly))
        except InvalidGeometryException:
            pass
    
    #Clip to Estuary Oceanic testing
    def clipToEstuariesTest(self):
        '''
            Tests the following:
                no estuary overlap ('cliipped_shape == 'target_shape')
                overlaps both estuary and oceanic, oceanic returned
                overlaps both estuary and oceanic, estuary returned
                geometry not valid
                estuary only
                missing kwargs
        '''
        #mpa does not overlap with estuary
        response0 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code0_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response0.status_code, 200)
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code0_poly), estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 4, places=1)
    
        #overlaps both estuary and oceanic, oceanic returned
        response1 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code1_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response1.status_code, 200)
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code1_poly), estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 3.5, places=1)
        
        #overlaps both estuary and oceanic, estuary returned
        response5 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code5_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response5.status_code, 200)
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code5_poly), estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 1.5, places=1)
        
        #mpa is outside of study region (but this shouldn't matter much to ClipToEstuaries)
        response2 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code2_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response2.status_code, 200)
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code2_poly), estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 1, places=1)

        #mpa geometry is not valid
        response3 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code3_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response3.status_code, 200)
        try:
            graticule_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code3_poly))
        except InvalidGeometryException:
            pass
        
        #mpa is estuary only
        response4 = self.client.post('/manipulators/ClipToEstuaries/', {'target_shape': display_kml(self.code4_poly), 'estuaries': self.ests.wkt})
        self.assertEquals(response4.status_code, 200)
        #again with direct call to ClipToEstuariesManipulator.manipulate
        estuary_clipper = ClipToEstuariesManipulator(target_shape=display_kml(self.code4_poly), estuaries=self.ests)
        result = estuary_clipper.manipulate()
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToEstuaries/', {})
        self.assertEquals(response6.status_code, 500)
        try:
            ClipToEstuariesManipulator()
        except TypeError:
            pass
        
    #Multiple Manipulators testing 
    def multipleManipulatorTest(self):
        '''
            Tests the following:
                clip to study region and clip to estuaries manipulations
                clip to study region and clip to graticules manipulations
                
        '''
        #clip to study region and estuaries test
        response1 = self.client.post('/manipulators/ClipToStudyRegion,ClipToEstuaries/', {'target_shape': display_kml(self.code1_poly)})
        self.assertEquals(response1.status_code, 200)
        #clip to study region and clip to graticules test
        response1 = self.client.post('/manipulators/ClipToStudyRegion,ClipToGraticule/', {'target_shape': display_kml(self.code1_poly), 'east': .5})
        self.assertEquals(response1.status_code, 200)
    
    
    #Tests mpa geometries appropriate for the nc_mlpa study region 
    def clipToNCMLPATest(self):
        '''
            Tests the following:
                clipped to study region
        '''
        study_region = StudyRegion.objects.current().geometry 
        
        w = study_region.extent[0]
        s = study_region.extent[1]
        e = study_region.extent[2]
        n = study_region.extent[3]
        
        center_lat = study_region.centroid.y 
        center_lon = study_region.centroid.x
                
        target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))
        target_shape.set_srid(settings.GEOMETRY_DB_SRID)
        target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        
        #clip to study region
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': display_kml(target_shape)})
        self.assertEquals(response0.status_code, 200)
       
    
