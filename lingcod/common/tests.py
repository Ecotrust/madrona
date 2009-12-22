from django.test import TestCase

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

from md5 import md5

class SessionsTest(TestCase):
    def test_load_session(self):
        from lingcod.common.utils import load_session
        request = TestRequest()
        load_session(request, '0')
        self.assertEquals(request.session, None)
        load_session(request, md5('blah').hexdigest())
        self.assertEquals(request.session.__class__.__name__, 'SessionStore')