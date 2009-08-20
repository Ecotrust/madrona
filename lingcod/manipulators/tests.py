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
            code_status 0:  clipped to study region
            code_status 2:  outside study region
            code_status 3:  geometry not valid
            code_status 6:  missing kwargs
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
        self.clipToStudyRegionTest()
        self.clipToGraticuleTest()
        
    def manipulatorViewTest(self):
        '''
            test views.generic_manipulator_view
        '''
        
        trans_geom = StudyRegion.objects.all()[0].geometry
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
        response = self.client.post('/manipulators/ClipToGraticule/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"})
        self.assertEquals(response.status_code, 200)
        
        # test non-trivial multi manipulator case
        response = self.client.post('/manipulators/ClipToStudyRegion,ClipToGraticule/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
        # test reversed order of manipulators
        response = self.client.post('/manipulators/ClipToGraticule,ClipToStudyRegion/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
    def clipToStudyRegionTest(self):
        '''
            Tests the following:
            code_status 0:  clipped to study region
            code_status 2:  outside study region
            code_status 3:  geometry not valid
            code_status 6:  missing kwargs
        '''

        #clipped to study region 
        response0 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code0_poly.wkt, 'study_region': self.study_region.wkt})
        #is this (check status_code==200) really all I can do at this point?  
        self.assertEquals(response0.status_code, 200)
        json0 = serializers.json.simplejson.loads(response0.content)
        self.assertEquals(json0["status_code"], '0')
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=self.code0_poly.wkt, study_region=self.study_region.wkt)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        #thought there might be a problem with places needing to be equal to 1 here, but
        #I tested it independently and it returns the same 1.9552852... value as ClipToStudyRegionManipulator
        #just part of transforming and intersecting I reckon
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1) 
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)

        #outside of study region
        response2 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code2_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response2.status_code, 200)
        json2 = serializers.json.simplejson.loads(response2.content)
        self.assertEquals(json2["status_code"], '2')
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=self.code2_poly.wkt, study_region=self.study_region.wkt)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '2')
        self.assertEquals(result["clipped_shape"].area, 0)
        self.assertAlmostEquals(result["original_shape"].area, 1, places=1)

        #geometry not valid
        response3 = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': self.code3_poly.wkt, 'study_region': self.study_region.wkt})
        self.assertEquals(response3.status_code, 200)
        json3 = serializers.json.simplejson.loads(response3.content)
        self.assertEquals(json3["status_code"], '3')
        studyregion_clipper = ClipToStudyRegionManipulator(target_shape=self.code3_poly.wkt, study_region=self.study_region.wkt)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '3')
        self.assertEquals(result["clipped_shape"], None)
        self.assertAlmostEquals(result["original_shape"].area, 0, places=7)
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToStudyRegion/', {'study_region': self.study_region.wkt})
        self.assertEquals(response6.status_code, 200)
        json6 = serializers.json.simplejson.loads(response6.content)
        self.assertEquals(json6["status_code"], '6')
        studyregion_clipper = ClipToStudyRegionManipulator(study_region=self.study_region.wkt)
        result = studyregion_clipper.manipulate()
        self.assertEquals(result["status_code"], '6')
        self.assertEquals(result["clipped_shape"], None)
        self.assertEquals(result["original_shape"], None)
    
        
    def clipToGraticuleTest(self):
        '''
            Tests the following:
            code_status 0:  clipped to graticule
            code_status 2:  clipping produced an empty geometry
            code_status 3:  geometry not valid
            code_status 4:  failed to create graticule clipped geometry
            code_status 6:  missing kwargs
        '''
        #clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'e': .5, 'w': -.5})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '0')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, e=.5, w=-.5)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        
        #another clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'n': .5, 's': -.5})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '0')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, n=.5, s=-.5)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        
        #another clip to graticule test
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'w': 0})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '0')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, w=0)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 2, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        
        #test with bad graticule values
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt, 'w': 3})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '2')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly, w=3)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '2')
        self.assertAlmostEquals(result["clipped_shape"].area, 0, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        
        #test with no graticule values
        response1 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code1_poly.wkt})
        self.assertEquals(response1.status_code, 200)
        json1 = serializers.json.simplejson.loads(response1.content)
        self.assertEquals(json1["status_code"], '0')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code1_poly)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '0')
        self.assertAlmostEquals(result["clipped_shape"].area, 4, places=1)
        self.assertAlmostEquals(result["original_shape"].area, 4, places=7)
        
        #test with bad geometry
        response3 = self.client.post('/manipulators/ClipToGraticule/', {'target_shape': self.code3_poly.wkt})
        self.assertEquals(response3.status_code, 200)
        json3 = serializers.json.simplejson.loads(response3.content)
        self.assertEquals(json3["status_code"], '3')
        graticule_clipper = ClipToGraticuleManipulator(target_shape=self.code3_poly)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '3')
        self.assertEquals(result["clipped_shape"], None)
        self.assertAlmostEquals(result["original_shape"].area, 0, places=7)
        
        #missing kwargs
        response6 = self.client.post('/manipulators/ClipToGraticule/', {'e': 3, 'w': -3})
        self.assertEquals(response6.status_code, 200)
        json6 = serializers.json.simplejson.loads(response6.content)
        self.assertEquals(json6["status_code"], '6')
        graticule_clipper = ClipToGraticuleManipulator(e=3, w=-3)
        result = graticule_clipper.manipulate()
        self.assertEquals(result["status_code"], '6')
        self.assertEquals(result["clipped_shape"], None)
        self.assertEquals(result["original_shape"], None)