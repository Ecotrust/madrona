"""
Unit tests for staticmap rendering via mapnik
"""
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.models import User, Group
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from lingcod.common.test_settings_manager import SettingsTestCase as TestCase
from lingcod.common.utils import enable_sharing
from lingcod.staticmap.models import MapConfig
from lingcod.features.tests import TestMpa, TestArray


class StaticMapTest(TestCase):
    fixtures = ['example_data']

    def setUp(self):
        self.client = Client()

        # Create 3 users
        self.password = 'iluvmapnik'
        self.user = User.objects.create_user('user1', 'test@marinemap.org', password=self.password)
        self.user2 = User.objects.create_user('user2', 'test@marinemap.org', password=self.password)
        
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        self.user.groups.add(self.group1)
        self.user2.groups.add(self.group1)
        enable_sharing(self.group1)
        self.public = Group.objects.get(name=settings.SHARING_TO_PUBLIC_GROUPS[0])
        self.user.groups.add(self.public)

        # Create some necessary objects
        g1 = GEOSGeometry('SRID=4326;POLYGON((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)

        # Create 3 Mpas by different users
        mpa1 = TestMpa.objects.create( name='Test_MPA_1', designation='R', user=self.user, geometry_orig=g1)
        mpa1.save()
        mpa2 = TestMpa.objects.create( name='Test_MPA_2', designation='P', user=self.user, geometry_orig=g1)
        mpa2.save()
        mpa3 = TestMpa.objects.create( name='Test_MPA_3', designation='C', user=self.user, geometry_orig=g1)
        mpa3.save()
        self.mpa_ids = [mpa1.pk, mpa2.pk, mpa3.pk]
        self.mpa_uids = ['%s_%s' % (mpa1.model_uid(), x) for x in self.mpa_ids]

        # User1 adds mpa to an array
        array1 = TestArray.objects.create( name='Test_Array_1', user=self.user)
        array1.save()
        array2 = TestArray.objects.create( name='Test_Array_2', user=self.user)
        array2.save()
        mpa1.add_to_collection(array1)
        mpa2.add_to_collection(array2)

        array1.share_with(self.group1)
        array2.share_with(self.public)

        self.array_ids = [array1.pk, array2.pk]
        self.array_uids = ['%s_%s' % (array1.model_uid(), x) for x in self.array_ids]

    def testMapConfigPresent(self):
        """
        Check presence of initial MapConfig
        """
        self.assertTrue(MapConfig.objects.count() > 0)

    def testMap(self):
        response = self.client.get('/staticmap/default/', {})
        self.assertEquals(response.status_code, 200)
        blank_map = response.content
        
        # User 1 should see these
        self.client.login(username=self.user.username, password=self.password)
        uidcsv = ','.join(self.mpa_uids)
        url = '/staticmap/default/?uids=%s' % uidcsv
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        #self.assertNotEquals(response.content, blank_map, 'Blank map == uids map for user 1. this should not be')

    def test_inaccessible(self):
        response = self.client.get('/staticmap/default/', {})
        self.assertEquals(response.status_code, 200)
        blank_map = response.content
        
        # User 2 shouldnt have access to mpa3
        self.client.login(username=self.user2.username, password=self.password)
        response = self.client.get('/staticmap/default/?uids=%s' % self.mpa_uids[2], {})
        self.assertEquals(response.status_code, 200)
        #self.assertEquals(response.content, blank_map)
 
    def test_sharing(self):
        response = self.client.get('/staticmap/default/', {})
        self.assertEquals(response.status_code, 200)
        blank_map = response.content
        
        # User 2 should see these
        response = self.client.get('/staticmap/default/?uids=%s' % ','.join(self.mpa_uids), {})
        self.assertEquals(response.status_code, 200)
        #self.assertNotEqual(response.content, blank_map)

    def test_anon(self):
        response = self.client.get('/staticmap/default/', {})
        self.assertEquals(response.status_code, 200)
        blank_map = response.content
        
        # Anon user shouldnt have access to mpa3, but yes to mpa2
        response = self.client.get('/staticmap/default/?uids=%s' % self.mpa_uids[2], {})
        self.assertEquals(response.status_code, 200)
        #self.assertEquals(response.content, blank_map)
        response = self.client.get('/staticmap/default/?uids=%s' % self.mpa_uids[1], {})
        self.assertEquals(response.status_code, 200)
        #self.assertNotEquals(response.content, blank_map)
           
        
