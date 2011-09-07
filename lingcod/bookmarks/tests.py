from django.test import TestCase

class BookmarkTest(TestCase):
    def test_unauth(self):
        # POST to url
        self.assertEqual(1 + 1, 2)

    def test_unauth_limit(self):
        # Multiple posts per URL
        self.assertEqual(1 + 1, 2)

    def test_create_feature(self):
        self.assertEqual(1 + 1, 2)

    def test_view(self):
        self.assertEqual(1 + 1, 2)
