"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from madrona.layer_manager import *
from madrona.layer_manager.models import Theme, Layer
import simplejson

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class LayerManagerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.theme1 = Theme.objects.create(name="Theme1")
        self.layer1 = Layer.objects.create(name="Layer1", layer_type='XYZ', url='https://s3.amazonaws.com/marco-public-2d/Test/ocsb2/ocsb/${z}/${x}/${y}.png')
        self.layer1.themes.add(self.theme1)
        self.client.login(username='layertest', password='pword')
	
    def test_layer_manager(self):	
        url = '/layer_manager/get_json'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, response.status_code)
        res_str = response.content + ','
        obj = simplejson.loads('[%s]' % res_str[:-1])
        self.assertEqual(obj[0]["themes"][0]["layers"][0], self.layer1.id, obj[0]["themes"][0]["layers"][0])
        self.assertEqual(obj[0]["state"]["activeLayers"], [], obj[0]["state"]["activeLayers"])
        self.assertEqual(obj[0]["themes"][0]["name"], "Theme1", obj[0]["themes"][0]["name"])
        self.assertEqual(obj[0]["themes"][0]["layers"], [1], obj[0]["themes"][0]["layers"])
