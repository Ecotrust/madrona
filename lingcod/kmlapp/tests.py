"""
Unit tests for the KML App
"""
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import *
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
from lingcod.common.utils import kml_errors

Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

class KMLAppTest(TestCase):
    def setUp(self):
        self.client = Client() 
        self.password = 'iluvge'
        self.user = User.objects.create_user('kmltest', 'kmltest@marinemap.org', password=self.password)

        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g2 = GEOSGeometry('SRID=4326;POLYGON ((-121.42 34.37, -120.64 34.32, -120.63 34.12, -121.44 34.15, -121.42 34.37))')
        g3 = GEOSGeometry('SRID=4326;POLYGON ((-122.42 34.37, -121.64 34.32, -121.63 34.12, -122.44 34.15, -122.42 34.37))')

        g1.transform(settings.GEOMETRY_DB_SRID)
        g2.transform(settings.GEOMETRY_DB_SRID)
        g3.transform(settings.GEOMETRY_DB_SRID)

        smr = MpaDesignation.objects.create(name="Reserve of some sort", acronym="R")
        smr.save()

        mpa1 = Mpa.objects.create( name='Test_MPA_1', designation=smr, user=self.user, geometry_final=g1)
        mpa2 = Mpa.objects.create( name='Test_MPA_2', designation=smr, user=self.user, geometry_final=g2)
        mpa3 = Mpa.objects.create( name='Test_MPA_3', designation=smr, user=self.user, geometry_final=g3)
        mpa1.save()
        mpa2.save()
        mpa3.save()
        self.test_mpa_id = mpa1.id

        array1 = MpaArray.objects.create( name='Test_Array_1', user=self.user)
        array1.save()
        self.test_array_id = array1.id
        array1.add_mpa(mpa1)
        array1.add_mpa(mpa2)

    def test_nonauth_user_kml(self):
        """ 
        Tests that non-authenticated user can't retrieve any MPAs
        """
        response = self.client.get('/kml/%s/user_mpa.kml' % self.user.username, {})
        errors = kml_errors(response.content)
        self.assertEquals(response.status_code, 401)

    def test_other_user_kml(self):
        """ 
        Tests that an authenticated user can't retrieve another user's MPAs
        """
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username=other_user.username, password='pword')
        response = self.client.get('/kml/%s/user_mpa.kml' % self.user.username, {})
        errors = kml_errors(response.content)
        self.assertEquals(response.status_code, 401)

    def test_user_kml(self):
        """ 
        Tests that user can retrieve valid KML file of their MPAs
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('/kml/%s/user_mpa.kml' % self.user.username, {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    
    def test_array_kml(self):
        """ 
        Tests that Array can be represented as valid KML
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('/kml/%d/array.kml' % self.test_array_id, {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_single_kml(self):
        """ 
        Tests that single MPA can be represented as valid KML
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('/kml/%d/mpa.kml' % self.test_mpa_id, {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_user_kmz_links(self):
        """ 
        Tests that user can retrieve valid KML file with network links to arrays
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('/kml/%s/user_mpa_links.kml' % self.user.username, {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_kmz_view(self):
        """ 
        Tests that we can retrieve a zipped KML file (ie KMZ)
        """
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('/kml/%s/user_mpa.kmz' % self.user.username, {})
        self.assertEquals(response.status_code, 200)
