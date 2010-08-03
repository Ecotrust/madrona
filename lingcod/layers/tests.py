"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.files import File
from lingcod.layers.models import PublicLayerList, PrivateLayerList
from lingcod.sharing.models import share_object_with_group, ShareableContent, get_shareables
from lingcod.sharing.utils import can_user_view
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.test.client import Client
from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse
import os

urlpatterns = patterns('',
    # Example:
    (r'^layers/', include('lingcod.layers.urls')),
)

class PrivateLayerListTest(TestCase):
    urls = 'lingcod.layers.tests'

    def setUp(self):
        # kml file
        kml_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures/public_layers.kml')

        # Create shareable content type
        ct = ContentType.objects.get_for_model(PrivateLayerList)
        share = ShareableContent.objects.create(shared_content_type=ct)
        share.save()

        # Create 3 users
        self.password = 'iluvsharing'
        self.user1 = User.objects.create_user('user1', 'test@marinemap.org', password=self.password)
        self.user2 = User.objects.create_user('user2', 'test@marinemap.org', password=self.password)
        self.user3 = User.objects.create_user('user3', 'test@marinemap.org', password=self.password)
       
        # Create some groups
        # Group 1 has user1 and user2 and can share
        group1 = Group.objects.create(name="Test Group 1")
        group1.save()
        self.group1_id = group1.id
        self.user1.groups.add(group1)
        self.user2.groups.add(group1)
        shareables = get_shareables()
        for modelname in shareables.iterkeys():
            group1.permissions.add(shareables[modelname][1])

        path = os.path.dirname(os.path.abspath(__file__))
        f = File(open(kml_path))
        settings.MEDIA_URL = ''
        
        # User1 creates Layer1 and shares with Group1
        layer1 = PrivateLayerList.objects.create(user=self.user1)
        layer1.save()
        layer1.kml.save('layer1.kml', f)
        self.layer1_id = layer1.pk
        share_object_with_group(layer1, group1)

        # User2 creates Layer2 and doesnt share (the selfish bastard)
        layer2 = PrivateLayerList.objects.create(user=self.user2)
        layer2.save()
        layer2.kml.save('layer2.kml', f)
        self.layer2_id = layer2.pk

    def test_permissions(self):
        # User 1 can view Layer 1
        self.assertTrue(can_user_view(PrivateLayerList,self.layer1_id,self.user1)[0])

        # User 2 can view Layer 1 (both members of shared group)
        self.assertTrue(can_user_view(PrivateLayerList,self.layer1_id,self.user2)[0])

        # User 3 can't view Layer 1
        self.assertFalse(can_user_view(PrivateLayerList,self.layer1_id,self.user3)[0])
        
        # User 1 can't view Layer 2 (User 2 hasnt shared it)
        self.assertFalse(can_user_view(PrivateLayerList,self.layer2_id,self.user1)[0])

        # User 2 can view Layer 2 (owns it)
        self.assertTrue(can_user_view(PrivateLayerList,self.layer2_id,self.user2)[0])

        # User 3 can't view Layer 2
        self.assertFalse(can_user_view(PrivateLayerList,self.layer2_id,self.user3)[0])

    def test_webservice(self):
        url = reverse('layers-private', kwargs={'pk': self.layer1_id, 'session_key': 0})

        self.client.login(username=self.user1, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username=self.user2, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()

        self.client.login(username=self.user3, password=self.password)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

        url = reverse('layers-private', kwargs={'pk': 982345, 'session_key': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_webservice_multi(self):

        self.client.login(username=self.user2, password=self.password)
        url = reverse('layers-all-for-user', kwargs={'session_key': 0})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        returned_urls = response.content.split(',') # TODO the parsing will change
        self.assertEqual(len(returned_urls),2) # the one shared and the one he owns
        for rurl in returned_urls:
            response = self.client.get(rurl.strip())
            self.assertEqual(response.status_code, 200)

        self.client.logout()



class PublicLayerListTest(TestCase):
    fixtures = ['example_data']

    def testCreate(self):
        """
        Test saving an instance of PublicLayerList to the repository
        """
        layer = PublicLayerList.objects.create(active=True)
        path = os.path.dirname(os.path.abspath(__file__))

        f = File(open(path + '/fixtures/public_layers.kml'))
        settings.MEDIA_URL = ''
        layer.kml.save('kml-file.kml', f)
        # 2 because the initial_data fixture loads one
        self.assertEquals(PublicLayerList.objects.count(), 2)
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
        l = PublicLayerList.objects.get(pk=1)
        # deactivate the fixture so it doesn't interfere with the test
        l.active = False
        l.save()
        response = client.get('/layers/public/')
        self.failUnlessEqual(response.status_code, 404)
        l.active = True
        l.save()
        # Create a layer to grab from the public layers service
        layer = PublicLayerList.objects.create(active=True)
        path = os.path.dirname(os.path.abspath(__file__))
        f = File(open(path + '/fixtures/public_layers.kml'))
        settings.MEDIA_URL = ''
        layer.kml.save('kml-file.kml', f)
        self.assertEquals(PublicLayerList.objects.count(), 2)
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

