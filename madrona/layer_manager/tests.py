from django.test import TestCase
from django.test.client import Client
from madrona.layer_manager.models import Theme, Layer
import simplejson

class LayerManagerTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/layer_manager/layers.json'
        self.theme1 = Theme.objects.create(name="Theme1")
        self.layer1 = Layer.objects.create(name="Layer1", layer_type='XYZ', 
                url='https://example.com/ocsb1/ocsb/${z}/${x}/${y}.png')
        self.layer1.themes.add(self.theme1)
        self.layer1_id = self.layer1.id
        self.layer2 = Layer.objects.create(name="Layer2", layer_type='XYZ', 
                url='https://example.com/ocsb2/ocsb/${z}/${x}/${y}.png')
        self.layer2.themes.add(self.theme1)
        self.layer2_id = self.layer2.id
	
    def test_themes(self):	
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.status_code)
        res_str = response.content
        obj = simplejson.loads(res_str)
        self.assertEqual(obj["state"]["activeLayers"], [], obj)
        self.assertEqual(obj["themes"][0]["name"], "Theme1", obj)
        self.assertEqual(obj["themes"][0]["layers"], [self.layer1_id, self.layer2_id])

    def test_state(self):	
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        res_str = response.content
        obj = simplejson.loads(res_str)
        self.assertEqual(obj["state"]["activeLayers"], [], obj)

    def test_layers(self):	
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200, response.status_code)
        res_str = response.content
        obj = simplejson.loads(res_str)
        self.assertEqual(obj["layers"][0]["name"], "Layer1")
        for layerid in obj["themes"][0]["layers"]:
            # make sure we can get the specified layer through the ORM
            lyr = Layer.objects.get(id=layerid)
