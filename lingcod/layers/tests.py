"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.files import File
from lingcod.layers.models import PublicLayerList
import os
from django.conf import settings
from django.test.client import Client
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'/layers/', include('lingcod.layers.urls')),
)


class PublicLayerListTest(TestCase):
    def testCreate(self):
        """
        Test saving an instance of PublicLayerList to the repository
        """
        layer = PublicLayerList.objects.create(active=True)
        path = os.path.dirname(os.path.abspath(__file__))

        f = File(open(path + '/fixtures/public_layers.kml'))
        settings.MEDIA_URL = ''
        layer.kml.save('kml-file.kml', f)
        self.assertEquals(PublicLayerList.objects.count(), 1)
        self.assertTrue(layer.kml.size > 0)
    
    def testOnlyOneActiveLayer(self):
        layer = PublicLayerList.objects.create(active=True)
        self.assertTrue(layer.active)
        # Create a new layer that is not active. Should not affect the current
        # active layer
        new_layer = PublicLayerList.objects.create(active=False)
        self.assertFalse(new_layer.active)
        active = PublicLayerList.objects.filter(active=True)
        self.assertEqual(active.count(), 1)
        self.assertEqual(active[0].pk, layer.pk)
        # Now create a new active layer. The first active layer should now 
        # be deactivated.
        new_active_layer = PublicLayerList.objects.create(active=True)
        active = PublicLayerList.objects.filter(active=True)
        self.assertEqual(active.count(), 1)
        self.assertEqual(active[0].pk, new_active_layer.pk)
    
    def testLayerService(self):
        urls = 'lingcod.layers.tests'
        # Should fail with a 404 when no layers are specified
        client = Client()
        response = client.get('/layers/public/')
        self.failUnlessEqual(response.status_code, 404)
        # Create a layer to grab from the public layers service
        layer = PublicLayerList.objects.create(active=True)
        path = os.path.dirname(os.path.abspath(__file__))
        f = File(open(path + '/fixtures/public_layers.kml'))
        settings.MEDIA_URL = ''
        layer.kml.save('kml-file.kml', f)
        self.assertEquals(PublicLayerList.objects.count(), 1)
        client = Client()
        response = client.get('/layers/public/')
        self.failUnlessEqual(response.status_code, 200)
    
    def tearDown(self):
        layer = PublicLayerList.objects.create(active=True)
        path = os.path.dirname(os.path.abspath(__file__))

        f = File(open(path + '/fixtures/public_layers.kml'))
        settings.MEDIA_URL = ''
        layer.kml.save('kml-file.kml', f)
        dr = os.path.dirname(layer.kml.file.name)
        cmd = 'rm -f %s/*.kml' % (dr, )
        os.system(cmd)
        
        
# __test__ = {"doctest": """
# """}

