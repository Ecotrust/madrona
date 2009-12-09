"""
Unit tests for the KML App
"""
from django.conf import settings
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import *
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
from lingcod.common.utils import kml_errors

Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

user = User.objects.get(username="default_user")

class KMLAppTest(TestCase):
    def setUp(self):
        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g2 = GEOSGeometry('SRID=4326;POLYGON ((-121.42 34.37, -120.64 34.32, -120.63 34.12, -121.44 34.15, -121.42 34.37))')
        g3 = GEOSGeometry('SRID=4326;POLYGON ((-122.42 34.37, -121.64 34.32, -121.63 34.12, -122.44 34.15, -122.42 34.37))')

        g1.transform(settings.GEOMETRY_DB_SRID)
        g2.transform(settings.GEOMETRY_DB_SRID)
        g3.transform(settings.GEOMETRY_DB_SRID)

        smr = MpaDesignation.objects.create(name="Reserve", acronym="R")
        smr.save()

        mpa1 = Mpa.objects.create( name='Test_MPA_1', user=user, geometry_final=g1)
        mpa2 = Mpa.objects.create( name='Test_MPA_2', designation=smr, user=user, geometry_final=g2)
        mpa3 = Mpa.objects.create( name='Test_MPA_3', designation=smr, user=user, geometry_final=g3)
        mpa1.save()
        mpa2.save()
        mpa3.save()

        array1 = MpaArray.objects.create( name='Test_Array_1', user=user)
        array1.save()
        array1.add_mpa(mpa1)

        array2 = MpaArray.objects.create( name='Test_Array_2', user=user)
        array2.save()
        array2.add_mpa(mpa2)

    def test_array_kml(self):
        """ 
        Tests that Array can be represented as valid KML
        """
        response = self.client.get('/kml/2/array.kml', {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_single_kml(self):
        """ 
        Tests that single MPA can be represented as valid KML
        """
        response = self.client.get('/kml/2/mpa.kml', {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_user_kml(self):
        """ 
        Tests that user can retrieve valid KML file of all users MPAs
        """
        response = self.client.get('/kml/default_user/user_mpa.kml', {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_user_kmz_links(self):
        """ 
        Tests that user can retrieve valid KML file with network links to arrays
        """
        response = self.client.get('/kml/default_user/user_mpa_links.kml', {})
        errors = kml_errors(response.content)
        if errors:
            raise Exception("Invalid KML\n%s" % str(errors))
        self.assertEquals(response.status_code, 200)

    def test_kmz_view(self):
        """ 
        Tests that we can retrieve a zipped KML file (ie KMZ)
        """
        response = self.client.get('/kml/default_user/user_mpa.kmz', {})
        self.assertEquals(response.status_code, 200)
