"""
Unit tests for staticmap rendering via mapnik
"""

from django.test import TestCase, Client
from django.conf.urls.defaults import *
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.contenttypes.models import ContentType
from lingcod.staticmap.models import *
from lingcod.mpa.models import Mpa, MpaDesignation
from lingcod.array.models import MpaArray
from lingcod.sharing.models import * 

from django.conf import settings

class StaticmapTestMpa(Mpa):
    extra_attr = models.CharField(max_length=255, blank=True)

class StaticmapTestArray(MpaArray):
    extra_attr = models.CharField(max_length=255, blank=True)

settings.MPA_CLASS = 'lingcod.staticmap.tests.StaticmapTestMpa'
settings.ARRAY_CLASS = 'lingcod.staticmap.tests.StaticmapTestArray'

class StaticMapTest(TestCase):
    def setUp(self):
        self.client = Client()

        # Create 3 users
        self.password = 'iluvmapnik'
        self.user = User.objects.create_user('user1', 'test@marinemap.org', password=self.password)
        self.client.login(username=self.user.username, password=self.password)
        
        # First register the mpas and arrays as shareable content types
        mpa_ct = ContentType.objects.get(app_label='staticmap',model='staticmaptestmpa')
        array_ct = ContentType.objects.get(app_label='staticmap',model='staticmaptestarray')

        share_mpa = ShareableContent.objects.create(shared_content_type=mpa_ct, 
                                                    container_content_type=array_ct,
                                                    container_set_property='mpa_set')
        share_array = ShareableContent.objects.create(shared_content_type=array_ct)

        # Create some necessary objects
        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)

        smr = MpaDesignation.objects.create(name="Reserve of some sort", acronym="R")
        smr.save()

        # Create 3 Mpas by different users
        mpa1 = StaticmapTestMpa.objects.create( name='Test_MPA_1', designation=smr, user=self.user, geometry_final=g1)
        mpa1.save()
        mpa2 = StaticmapTestMpa.objects.create( name='Test_MPA_2', designation=smr, user=self.user, geometry_final=g1)
        mpa2.save()
        mpa3 = StaticmapTestMpa.objects.create( name='Test_MPA_3', designation=smr, user=self.user, geometry_final=g1)
        mpa3.save()
        self.mpa_ids = [mpa1.pk, mpa2.pk, mpa3.pk]

        # User1 adds mpa to an array
        array1 = StaticmapTestArray.objects.create( name='Test_Array_1', user=self.user)
        array1.save()
        mpa1.add_to_array(array1)
        self.array_id = array1.id

    def testMapConfigPresent(self):
        """
        Check presence of initial MapConfig
        """
        self.assertTrue(MapConfig.objects.count() > 0)

    def testDefaultMap(self):
        """
        test default staticmap image response
        """
        response = self.client.get('/staticmap/default/', {})
        self.assertEquals(response.status_code, 200)
   
    def testMpaFilter(self):
        """
        See if mapnik filter can render a select list of MPAs using the filter
        """
        mpas = ','.join([str(x) for x in self.mpa_ids])
        response = self.client.get('/staticmap/default/?mpas=%s' % mpas, {})
        self.assertEquals(response.status_code, 200)

    def testArrayMap(self):
        """
        See if mapnik filter can render all mpas in a given array
        """
        response = self.client.get('/staticmap/default/?array=%s' % self.array_id, {})
        self.assertEquals(response.status_code, 200)
