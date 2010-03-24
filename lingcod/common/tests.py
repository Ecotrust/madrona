from django.test import TestCase
from django.conf import settings
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

