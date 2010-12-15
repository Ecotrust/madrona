from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.gis.geos import *
from lingcod.studyregion.models import StudyRegion
from django.core import serializers 
from manipulators import *      

urlpatterns = patterns('',
    (r'/manipulators/', include('lingcod.manipulators.urls')),
)

# set up some test manipulators
class TestManipulator(BaseManipulator):
    """ 
    This manipulator does nothing but ensure the geometry is clean. 
    """
    def __init__(self, target_shape, **kwargs):
        self.target_shape = target_shape

    def manipulate(self): 
        target_shape = self.target_to_valid_geom(self.target_shape)
        status_html = self.do_template("0")
        return self.result(target_shape, status_html)

    class Options(BaseManipulator.Options):
        name = 'TestManipulator'
        supported_geom_fields = ['PolygonField']
        html_templates = { '0':'manipulators/valid.html', }

manipulatorsDict[TestManipulator.Options.name] = TestManipulator        

class ManipulatorsTest(TestCase):
    fixtures = ['manipulators_test_data']

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
        
        
    def test_clipToGraticule(self):
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
    
    def test_clipToStudyRegion(self):
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
    
        
    def test_multipleManipulators(self):
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
    
    
    def test_studyregion(self):
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
       
    
