"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class LayerManagerTest(TestCase):
    def setUp(self):
        self.client = CLient()
        self.user = User.objects.create_user(
            'layertest', 'layertest@madrona.org', password='pword')
        self.layer1 = TestLayer.objects.create(user=self.user, name="Layer1")
	
    def test_layer_manager(self):
	
