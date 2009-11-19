from django.test import TestCase
from django.conf import settings
from django.core.files import File
#from lingcod.intersection.admin import *
from lingcod.intersection.models import *
import os

def upload_multifeature_poly(file_name='test_substrate.zip'):
    # upload polygon shapefile
    polygon_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', file_name)
    polygon_zip = open(polygon_zip_path)
    mfsf = MultiFeatureShapefile(name="test polygon", shapefile=File(polygon_zip) )
    mfsf.save()
    polygon_zip.close()
    
def upload_multifeature_line(file_name='test_shoretype.zip'):
    zip_path = os.path.join(os.path.dirname(__file__), 'test_data', file_name)
    zip_file = open(zip_path)
    mfsf = MultiFeatureShapefile(name="test linear", shapefile=File(zip_file) )
    mfsf.save()
    zip_file.close()
    
def upload_singlefeature_point(file_name='test_points.zip'):
    zip_path = os.path.join(os.path.dirname(__file__), 'test_data', file_name)
    zip_file = open(zip_path)
    sfsf = SingleFeatureShapefile(name="test points", shapefile=File(zip_file) )
    sfsf.save()
    zip_file.close()

class SumResultsTest(TestCase):
    def test_sum_results(self):
        summed = sum_results([[{'feature_name': u'test points','percent_of_total': 10,'result': 1.0,'sort': 0.5,'units': u'count'},{'feature_name': u'Beaches','percent_of_total': 0.2,'result': 1.0,'sort': 0.6,'units': u'miles'},{'feature_name': u'Rocky Shores','percent_of_total': 1.0,'result': 10.0,'sort': 0.7,'units': u'miles'}],[{'feature_name': u'test points','percent_of_total': 10,'result': 1.0,'sort': 0.5,'units': u'count'},{'feature_name': u'Beaches','percent_of_total': 0.2,'result': 1.0,'sort': 0.6,'units': u'miles'},{'feature_name': u'Rocky Shores','percent_of_total': 2.0,'result': 20.0,'sort': 0.7,'units': u'miles'}]])
        
        self.assertEquals(summed.__len__(),3)
        
        self.assertEquals(summed[0]['result'],2.0)
        self.assertEquals(summed[1]['result'],2.0)
        self.assertEquals(summed[2]['result'],30.0)
        
        self.assertEquals(summed[0]['percent_of_total'],20.0)
        self.assertEquals(summed[1]['percent_of_total'],0.40000000000000002)
        self.assertEquals(summed[2]['percent_of_total'],3.0)
        
class UploadShapefilesTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
            
    def tearDown(self):
        # The tests should delete these but just in case they don't they're deleted here
        # If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
    
    def test_multishapefile_upload(self):
        upload_multifeature_poly()
        
        # Check to make sure the shapefile has been added
        mfs = MultiFeatureShapefile.objects.get(name='test polygon')
        if mfs:
            it_is = True
        else:
            it_is = False
        self.assertTrue(it_is)
        # make sure the file has been put where it's supposed to be
        file_path = mfs.shapefile.path
        self.assertTrue( os.path.exists(file_path) )
        # make sure the file goes away when the feature is deleted
        mfs.delete()
        self.assertFalse( os.path.exists(file_path) )
        
    def test_singleshapefile_upload(self):
        # upload point shapefile
        upload_singlefeature_point()
        
        # Check to make sure the shapefile has been added
        sfs = SingleFeatureShapefile.objects.get(name='test points')
        if sfs:
            it_is = True
        else:
            it_is = False
        self.assertTrue(it_is)
        # make sure the file has been put where it's supposed to be
        file_path = sfs.shapefile.path
        self.assertTrue( os.path.exists(file_path) )
        # make sure the file goes away when the feature is deleted
        sfs.delete()
        self.assertFalse( os.path.exists(file_path) )
        
class SplitToSingleFeatureShapefilesTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
        # upload polygon shapefile
        upload_multifeature_poly()
        
        # upload a linear shapefile
        upload_multifeature_line()
        
        
    def tearDown(self):
#         The tests should delete these but just in case they don't they're deleted here
#         If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
        
    def test_poly_multi_split_to_single(self):
        sfshp = MultiFeatureShapefile.objects.get(name='test polygon')
        sfshp.split_to_single_feature_shapefiles('sub_depth')
        
        self.assertEquals( SingleFeatureShapefile.objects.all().count(), 11)
        for sfs in SingleFeatureShapefile.objects.filter(parent_shapefile=MultiFeatureShapefile.objects.get(name='test polygon')):
            # make sure the file is where it's supposed to be
            file_path = sfs.shapefile.path
            self.assertTrue( os.path.exists(file_path) )
            # make sure the file goes away when the feature is deleted
            sfs.delete()
            self.assertFalse( os.path.exists(file_path) )
            
    def test_linear_multi_split_to_single(self):
        sfshp = MultiFeatureShapefile.objects.get(name='test linear')
        sfshp.split_to_single_feature_shapefiles('mapclass')
        
        self.assertEquals( SingleFeatureShapefile.objects.all().count(), 2)
        for sfs in SingleFeatureShapefile.objects.all():
            # make sure the file is where it's supposed to be
            file_path = sfs.shapefile.path
            self.assertTrue( os.path.exists(file_path) )
            # make sure the file goes away when the feature is deleted
            sfs.delete()
            self.assertFalse( os.path.exists(file_path) )
            
class ImportShapefileFeaturesToDbTest(TestCase):
    fixtures = ['minimal_test_data.json']
    def setUp(self):
        # log in
        if self.client.login(username='test',password='testing'):
            print 'login worked'
        else:
            print 'login failed!!!!!!!!!!!!!!!!'
        # upload polygon shapefile
        upload_multifeature_poly()
        
        # upload a linear shapefile
        upload_multifeature_line()
        
        # split polygon multi features into single feature shapefiles
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test polygon').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'sub_depth' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        
        # split linear multi features in single feature shapefiles
        mfshp_pk = MultiFeatureShapefile.objects.get(name='test linear').pk
        form_data = { 'mfshp_pk': mfshp_pk, 'shp_field': 'mapclass' }
        action_url = '/admin/intersection/multifeatureshapefile/%i/splitonfield/' % mfshp_pk
        response = self.client.post(action_url, form_data)
        
        # upload point shapefile
        point_zip_path = os.path.join(os.path.dirname(__file__), 'test_data', 'test_points.zip')
        point_zip = open(point_zip_path)
        form_data = { 'shapefile' : point_zip, 'name' : 'test points', 'shapefilefield_set-TOTAL_FORMS' : 0, 'shapefilefield_set-INITIAL_FORMS' : 0 }
        response = self.client.post('/admin/intersection/singlefeatureshapefile/add/', form_data)
        point_zip.close()
        
    def tearDown(self):
#         The tests should delete these but just in case they don't they're deleted here
#         If they are not deleted, they leave zipped shapefiles sitting around
        MultiFeatureShapefile.objects.all().delete()
        SingleFeatureShapefile.objects.all().delete()
        
    def test_shapefiles_to_features(self):
        for shape in SingleFeatureShapefile.objects.all():
            shape.load_to_features()
            # make sure features exist
            if IntersectionFeature.objects.filter(name=shape.name):
                result = True
                int_feat = IntersectionFeature.objects.get(name=shape.name)
            else:
                result = False
            self.assertTrue(result)
            if not result:
                return False
            
            # make sure that geometries exist for the feature
            geom_set = int_feat.geometries_set
            if geom_set:
                result = True
            else:
                result = False
            self.assertTrue(result)
            
class RunIntersectionsWithTestPolygonTest(TestCase):
    fixtures = ['with_test_data_loaded.json']
#    def setUp(self):
        # log in
#        if self.client.login(username='test',password='testing'):
#            print 'login worked'
#        else:
#            print 'login failed!!!!!!!!!!!!!!!!'
            
    def test_default_intersection_with_test_polygon(self):
        import pickle
        
        tp = TestPolygon.objects.all()[0]
        result = intersect_the_features(tp.geometry)
        
        pickle_path = os.path.join(os.path.dirname(__file__), 'test_data', 'default_tp1_result.pickle')
        f = open(pickle_path, 'rb')
        pickled_result = pickle.load(f)
        f.close()
        
        keys = pickled_result[0].keys()
        for i in range(0,pickled_result.__len__() ):
            for key in keys:
                if key=='result' or key=='percent_of_total':
                    self.assertEqual(round(result[i][key],7),round(pickled_result[i][key],7))
                else:
                    self.assertEqual(result[i][key],pickled_result[i][key])
                       
    def test_ordered_intersection_with_test_polygon(self):
        import pickle
        
        osc = OrganizationScheme.objects.get(name='Nice Order')
        tp = TestPolygon.objects.all()[0]
        result = osc.transformed_results(tp.geometry)
        
        pickle_path = os.path.join(os.path.dirname(__file__), 'test_data', 'nice_order_tp1_result.pickle')
        f = open(pickle_path, 'rb')
        pickled_result = pickle.load(f)
        f.close()
        
        keys = pickled_result[0].keys()
        for i in range(0,pickled_result.__len__() ):
            for key in keys:
                if key=='result' or key=='percent_of_total':
                    self.assertEqual(round(result[i][key],7),round(pickled_result[i][key],7))
                else:
                    self.assertEqual(result[i][key],pickled_result[i][key])
