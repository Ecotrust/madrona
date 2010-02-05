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

class BrowserUserAgentTest(TestCase):
    def setUp(self):
        self.supported_uastring_examples = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-us) AppleWebKit/531.21.8 (KHTML, like Gecko) Version/4.0.4 Safari/531.21.10',
        ]

        self.unsupported_uastring_examples = [
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_2; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.49 Safari/532.5',
        ]

    def test_supported_browsers(self):
        from lingcod.common.utils import valid_browser 
        for ua in self.supported_uastring_examples:
            self.assertEquals(valid_browser(ua),True)

    def test_unsupported_browsers(self):
        from lingcod.common.utils import valid_browser 
        for ua in self.unsupported_uastring_examples:
            self.assertEquals(valid_browser(ua),False)



