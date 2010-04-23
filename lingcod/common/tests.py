from django.test import TestCase
from django.conf import settings
from django.contrib.gis import geos
from lingcod.common.utils import *
import os

class AssetsTest(TestCase):
    def test_get_js_files(self):
        """
        Should return a list of javascript files from 
        media/common/js_includes.xml
        """
        from lingcod.common import assets
        files = assets.get_js_files()
        self.assertEquals(files.__class__.__name__, 'list')
        self.assertTrue(len(files) > 0)

    def test_get_css_files(self):
        """
        Should return a list of stylesheets from media/common/css_includes.xml
        """
        from lingcod.common import assets
        files = assets.get_css_files()
        self.assertEquals(files.__class__.__name__, 'list')
        self.assertTrue(len(files) > 0)

class TestRequest:
    session = None
    
class UtilsTest(TestCase):
    def test_angle_method(self):
        # try without srids
        pnt1 = Point(1,0)
        pnt2 = Point(0,0)
        pnt3 = Point(0,1)
        result = angle(pnt1,pnt2,pnt3)
        self.assertEquals(result,1.5707963267949001)
        
        # with srids
        pnt1.srid = 3310
        pnt2.srid = 3310
        pnt3.srid = 3310
        result2 = angle(pnt1,pnt2,pnt3)
        self.assertEquals(result2,1.5707963267949001)
        
    def test_spike_ring_indecies(self):
        poly = geos.fromstr('POLYGON((3480407.01 5483810.171,3480407.01 5483810.17,3480409.11 5483777.431,3480407.348 5483777.421,3480405.15 5483777.409,3480404.816 5483777.407,3480394.58 5483777.35,3480395.36 5483811.12,3480404.55 5483810.46,3480405.951 5483810.295,3480406.312 5483795.106,3480405.951 5483810.296,3480406.903 5483810.184,3480407.01 5483810.171))')
        indecies = spike_ring_indecies(poly.exterior_ring, 0.01)
        self.assertEquals(indecies[0],10)
        
    def test_remove_spikes(self):
        poly = geos.fromstr('POLYGON ((3415632.4900000002235174 5291021.4900000002235174, 3415632.4879999998956919 5291021.4939999999478459, 3415632.4900000002235174 5291021.4939999999478459, 3415628.9300000001676381 5291028.2800000002607703, 3415642.9500000001862645 5291001.5599999995902181, 3415651.1800000001676381 5290985.8600000003352761, 3415659.2700000000186265 5290984.6100000003352761, 3415644.7099999999627471 5290947.8099999995902181, 3415629.1699999999254942 5290921.8300000000745058, 3415621.2799999997951090 5290929.7199999997392297, 3415640.2099999999627471 5290959.4299999997019768, 3415625.3799999998882413 5290971.4100000001490116, 3415627.7900000000372529 5290983.9400000004097819, 3415629.4900000002235174 5290992.1900000004097819, 3415630.1400000001303852 5290995.3600000003352761, 3415625.6499999999068677 5291022.5000000000000000, 3415632.4900000002235174 5291021.4900000002235174))')
        result = remove_spikes(poly, 0.01)
        expected_wkt = 'POLYGON ((3415632.4900000002235174 5291021.4900000002235174, 3415632.4879999998956919 5291021.4939999999478459, 3415632.4900000002235174 5291021.4939999999478459, 3415642.9500000001862645 5291001.5599999995902181, 3415651.1800000001676381 5290985.8600000003352761, 3415659.2700000000186265 5290984.6100000003352761, 3415644.7099999999627471 5290947.8099999995902181, 3415629.1699999999254942 5290921.8300000000745058, 3415621.2799999997951090 5290929.7199999997392297, 3415640.2099999999627471 5290959.4299999997019768, 3415625.3799999998882413 5290971.4100000001490116, 3415627.7900000000372529 5290983.9400000004097819, 3415629.4900000002235174 5290992.1900000004097819, 3415630.1400000001303852 5290995.3600000003352761, 3415625.6499999999068677 5291022.5000000000000000, 3415632.4900000002235174 5291021.4900000002235174))'
        self.assertEquals(result.wkt,expected_wkt)
        result = remove_spikes(result, 0.01)
        self.assertEquals(result,expected_wkt)

from django.utils.hashcompat import md5_constructor as md5

class SessionsTest(TestCase):
    def test_load_session(self):
        from lingcod.common.utils import load_session
        request = TestRequest()
        load_session(request, '0')
        self.assertEquals(request.session, None)
        load_session(request, md5('blah').hexdigest())
        self.assertEquals(request.session.__class__.__name__, 'SessionStore')

class BrowserUserAgentTest(TestCase):
    def setUp(self):
        exdir = os.path.dirname(os.path.abspath(__file__))
        self.supported_uastring_examples = [x.strip() for x in open(exdir + '/supported_user_agent_examples.txt').readlines()]
        self.unsupported_uastring_examples = [x.strip() for x in open(exdir + '/unsupported_user_agent_examples.txt').readlines()]

    def test_supported_browsers(self):
        from lingcod.common.utils import valid_browser 
        for ua in self.supported_uastring_examples:
            if not valid_browser(ua):
                print "UAPARSER SAYS NOT SUPPORTED ....." , ua
            self.assertEquals(valid_browser(ua),True)

    def test_unsupported_browsers(self):
        from lingcod.common.utils import valid_browser 
        for ua in self.unsupported_uastring_examples:
            if valid_browser(ua):
                print "UAPARSER SAYS SUPPORTED ....." , ua
            self.assertEquals(valid_browser(ua),False)

class AccessTest(TestCase):
    
    def test_upload_dir_access(self):
        """ Ensure that the upload directory is not web accessible """

        url = settings.MEDIA_URL + 'upload/' 
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403, url)

        url = settings.MEDIA_URL + 'upload/test.txt' 
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403, url)

        url = settings.MEDIA_URL + '/upload/test.txt' 
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403, url)

        url = settings.MEDIA_URL + '/./upload/test.txt' 
        response = self.client.get(url)
        self.assertEquals(response.status_code, 403, url)

class InstalledAppTest(TestCase):

    def test_dup_app_labels(self):
        """ Make sure we dont have any apps with duplicate app_labels
        for the sake of south, contenttypes and any other django piece
        which relies on app_label """

        labels = [x.split('.')[-1] for x in settings.INSTALLED_APPS]
        counts = {}
        for label in labels:
            if label not in counts.keys():
                counts[label] = 1
            else:
                counts[label] += 1

        for k,v in counts.items():
            self.assertEquals(v, 1, 'app_label %s refers to %s apps' % (k,v))

class DependenciesTest(TestCase):

    def test_dependencies(self):
        imports = [ 
            'networkx',
            'south',
            'django.contrib.gis',
            'elementtree',
            'sphinx',
            'mapnik',
            'feedvalidator',
            'BeautifulSoup',
            'xlwt',
            'registration',
            'compress',
            'maintenancemode',
        ]
        from django.utils import importlib
        for dep in imports:
            try:
                m = importlib.import_module(dep)
            except:
                m = None
            self.assertNotEquals(m,None,'Cannot import %s' % dep)


