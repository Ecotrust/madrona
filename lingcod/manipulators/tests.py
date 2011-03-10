from django.test import TestCase
from django.test.client import Client
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.gis.geos import *
from lingcod.studyregion.models import StudyRegion
from django.core import serializers 
from manipulators import *      
from lingcod.features.models import Feature, PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.features.forms import FeatureForm
from lingcod.features import register
from django.contrib.auth.models import User

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
       
    
@register
class TestPoly(PolygonFeature):
    type = models.CharField(max_length=1)
    class Options:
        verbose_name = 'Test Poly'
        form = 'lingcod.manipulators.tests.TestPolyForm'
        manipulators = [ 'lingcod.manipulators.manipulators.ClipToStudyRegionManipulator' ]
class TestPolyForm(FeatureForm):
    class Meta:
        model = TestPoly

@register
class TestOptmanip(PolygonFeature):
    type = models.CharField(max_length=1)
    class Options:
        verbose_name = 'Feature to Test Optional Manipulators'
        form = 'lingcod.manipulators.tests.TestOptmanipForm'
        optional_manipulators = [ 'lingcod.manipulators.manipulators.ClipToStudyRegionManipulator' ]
        manipulators = []
class TestOptmanipForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = TestOptmanip

@register
class TestLine(LineFeature):
    type = models.CharField(max_length=1)
    diameter = models.FloatField(null=True)
    class Options:
        verbose_name = 'TestLine'
        form = 'lingcod.manipulators.tests.TestLineForm'
        manipulators = [ 'lingcod.manipulators.manipulators.ClipToStudyRegionManipulator' ]
class TestLineForm(FeatureForm):
    class Meta:
        model = TestLine

@register
class TestPoint(PointFeature):
    incident = models.CharField(max_length=1)
    class Options:
        verbose_name = 'TestPoint'
        form = 'lingcod.manipulators.tests.TestPointForm'
        manipulators = [ 'lingcod.manipulators.manipulators.ClipToStudyRegionManipulator' ]
class TestPointForm(FeatureForm):
    class Meta:
        model = TestPoint

class FeaturesManipulatorTest(TestCase):
    fixtures = ['example_data']

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            'featuretest', 'featuretest@marinemap.org', password='pword')
        self.client.login(username='featuretest', password='pword')

    def test_point_outside(self):
        from lingcod.manipulators.manipulators import ClipToStudyRegionManipulator as csrm
        with self.assertRaisesRegexp(csrm.HaltManipulations, 'empty'):
            g = GEOSGeometry('SRID=4326;POINT(-100.45 14.32)')
            g.transform(settings.GEOMETRY_DB_SRID)
            feature = TestPoint(user=self.user, name="Outside Region", geometry_orig=g)
            feature.save()

    def test_studyregion_point(self):
        g = GEOSGeometry('SRID=4326;POINT(-119.82 34.404)')
        g.transform(settings.GEOMETRY_DB_SRID)
        feature = TestPoint(user=self.user, name="Nearby Wreck", geometry_orig=g)
        feature.save()
        self.assertEqual(g, feature.geometry_final)

    def test_studyregion_line_allin(self):
        # all in
        g = GEOSGeometry('SRID=4326;LINESTRING(-120.234 34.46, -120.152 34.454)')
        g.transform(settings.GEOMETRY_DB_SRID)
        feature = TestLine(user=self.user, name="My Pipeline", geometry_orig=g)
        feature.save()
        # floating point imprecission .. can't do this
        # self.assertTrue(g.equals(feature.geometry_final))
        self.assertAlmostEquals(g[1][0], feature.geometry_final[1][0])
        self.assertAlmostEquals(g[1][1], feature.geometry_final[1][1])

    def test_studyregion_line_partial(self):
        # partial 
        g = GEOSGeometry('SRID=4326;LINESTRING(-120.234 34.46, -120.162 34.547)')
        g.transform(settings.GEOMETRY_DB_SRID)
        feature = TestLine(user=self.user, name="My Pipeline", geometry_orig=g)
        feature.save()
        clip = GEOSGeometry('SRID=3310;LINESTRING (-21492.0524731723162404 -395103.6204170039854944, -20676.0969509799033403 -393916.9388333586975932)')
        self.assertAlmostEquals(clip[1][0], feature.geometry_final[1][0])
        self.assertAlmostEquals(clip[1][1], feature.geometry_final[1][1])

    def test_studyregion_poly_allin(self):
        # all in
        g = GEOSGeometry('SRID=4326;POLYGON((-120.161 34.441, -120.144 34.458, -120.186 34.455, -120.161 34.441))') 
        g.transform(settings.GEOMETRY_DB_SRID)
        feature = TestPoly(user=self.user, name="My Mpa", geometry_orig=g) 
        feature.save()
        self.assertAlmostEquals(g.area, feature.geometry_final.area, 2)
        
    def test_studyregion_poly_partial(self):
        #partial
        g = GEOSGeometry('SRID=4326;POLYGON((-120.234 34.46, -120.152 34.454, -120.162 34.547, -120.234 34.46))')
        g.transform(settings.GEOMETRY_DB_SRID)
        feature = TestPoly(user=self.user, name="My Mpa", geometry_orig=g) 
        feature.save()
        self.assertNotAlmostEquals(g.area, feature.geometry_final.area)

    def test_optional_manip_form(self):
        # TestPoly should NOT have any optional manipulators defined
        options = TestPoly.get_options()
        response = self.client.get(options.get_create_form())
        self.assertEqual(response.status_code, 200)
        self.assertNotRegexpMatches(response.content, r'optional_manipulators')

        # get the form and confirm that it allows cliptostudyregion as optional manip
        options = TestOptmanip.get_options()
        response = self.client.get(options.get_create_form())
        self.assertEqual(response.status_code, 200)
        self.assertRegexpMatches(response.content, r'optional_manipulators')
        self.assertRegexpMatches(response.content, r'ClipToStudyRegion')

    def test_optional_manip(self):
        # partial polygon
        g = GEOSGeometry('SRID=4326;POLYGON((-120.234 34.46, -120.152 34.454, -120.162 34.547, -120.234 34.46))')
        g.transform(settings.GEOMETRY_DB_SRID)

        orig_geom = '-120.234,34.46,700 -120.152,34.454,700 -120.162,34.547,700 -120.234,34.46,700'
        clip_geom = "-120.154031278,34.472909502,700 -120.152,34.454,700 -120.234,34.46,700 "\
                "-120.2251468,34.4707108689,700 -120.218519204,34.4709073104,700 -120.217006684,34.4706784357,700 "\
                "-120.21271897,34.4708157272,700 -120.208662028,34.4704036177,700 -120.203517908,34.4704151237,700 "\
                "-120.19793129,34.4707738014,700 -120.186931614,34.4698275471,700 -120.1839447,34.4706171748,700 "\
                "-120.177446368,34.4709301328,700 -120.168699263,34.4697474322,700 -120.165655133,34.4711589807,700 "\
                "-120.159605021,34.4716395135,700 -120.158477785,34.4722310096,700 -120.154031278,34.472909502,700"

        # Next, POST to manipulators url with no manipulators specified; should get original geom back
        response = self.client.post('/manipulators//', {'target_shape': display_kml(g)})
        self.assertTrue(orig_geom in response.content)
        self.assertFalse(clip_geom in response.content)

        # Next, POST to manipulators url with ClipToStudyRegionManipulator specified; should get clipped geom back
        response = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape': display_kml(g)})
        self.assertTrue(orig_geom in response.content)
        self.assertTrue(clip_geom in response.content)
