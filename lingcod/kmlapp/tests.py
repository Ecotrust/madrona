# -*- coding: utf-8 -*-
# ^^^ this is required on 1st or 2nd line; see http://www.python.org/dev/peps/pep-0263/
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
from django.core.urlresolvers import reverse

Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

class KMLAppTest(TestCase):
    fixtures = ['example_data']
    def setUp(self):
        self.client = Client()
        self.other_client = Client()
        self.password = 'iluvge'
        self.user = User.objects.create_user('kmltest', 'kmltest@marinemap.org', password=self.password)
        self.user2 = User.objects.create_user('kmltest2', 'kmltest2@marinemap.org', password=self.password)

        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g2 = GEOSGeometry('SRID=4326;POLYGON ((-121.42 34.37, -120.64 34.32, -120.63 34.12, -121.44 34.15, -121.42 34.37))')
        g3 = GEOSGeometry('SRID=4326;POLYGON ((-122.42 34.37, -121.64 34.32, -121.63 34.12, -122.44 34.15, -122.42 34.37))')

        g1.transform(settings.GEOMETRY_DB_SRID)
        g2.transform(settings.GEOMETRY_DB_SRID)
        g3.transform(settings.GEOMETRY_DB_SRID)

        smr = MpaDesignation.objects.create(name="Reserve of some sort", acronym="R")
        smr.save()

        mpa1 = Mpa.objects.create( name='Test_MPA_1', designation=smr, user=self.user, geometry_final=g1)
        mpa2 = Mpa.objects.create( name=u'Test_MPA_2_with_some_uniçode', designation=smr, user=self.user, geometry_final=g2)
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

        # Register the mpas and arrays as shareable content types
        from lingcod.sharing.models import ShareableContent
        from lingcod.sharing.utils import get_content_type, get_shareables
        mpa_ct = get_content_type(Mpa)
        array_ct = get_content_type(MpaArray)
        share_mpa = ShareableContent.objects.create(shared_content_type=mpa_ct, 
                                                    container_content_type=array_ct,
                                                    container_set_property='mpa_set')
        share_array = ShareableContent.objects.create(shared_content_type=array_ct)

        # Then make the group with permissions
        from django.contrib.auth.models import Group
        self.group1 = Group.objects.create(name="Test Group 1")
        self.group1.save()
        shareables = get_shareables()
        for modelname in shareables.iterkeys():
            self.group1.permissions.add(shareables[modelname][1])

        # Add users to group
        self.user.groups.add(self.group1)
        self.user2.groups.add(self.group1)

        # Share with common group
        from lingcod.sharing.utils import share_object_with_groups
        share_object_with_groups(array1, [self.group1.pk])

        # Share with public
        public_group = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)[0]
        for modelname in shareables.iterkeys():
            public_group.permissions.add(shareables[modelname][1])
        share_object_with_groups(array1, [public_group.pk])

    def test_nonauth_user_kml(self):
        """ 
        Tests that non-authenticated user can't retrieve any MPAs
        """
        url = reverse('kmlapp-user-kml', kwargs={'session_key': 0, 'input_username': self.user.username})
        response = self.client.get(url)
        errors = kml_errors(response.content)
        self.assertEquals(response.status_code, 401)

    def test_other_user_kml(self):
        """ 
        Tests that an authenticated user can't retrieve another user's MPAs
        """
        other_user = User.objects.create_user('other', 'other@marinemap.org', password='pword')
        self.client.login(username=other_user.username, password='pword')
        url = reverse('kmlapp-user-kml', kwargs={'session_key': 0, 'input_username': self.user.username})
        # response = self.client.get('/kml/%s/user_mpa.kml' % self.user.username, {})
        response = self.client.get(url)
        # errors = kml_errors(response.content)
        self.assertEquals(response.status_code, 401)
        # Test for same result using session_key in url
        self.client.logout()
        self.client.login(username=other_user.username, password='pword')
        url = reverse('kmlapp-user-kml', kwargs={'session_key': self.client.session.session_key, 'input_username': self.user.username})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 401)

    def test_user_kml(self):
        """ 
        Tests that user can retrieve valid KML file of their MPAs
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-user-kml', kwargs={'session_key': 0, 'input_username': self.user.username})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))
            
        # test for session key url
        url = reverse('kmlapp-user-kml', kwargs={'session_key': self.client.session.session_key, 'input_username': self.user.username})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 200)
    
    def test_array_kml(self):
        """ 
        Tests that Array can be represented as valid KML
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-array-kml', kwargs={'session_key': '0', 'input_array_id': self.test_array_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

        # test session_key in url method
        url = reverse('kmlapp-array-kml', kwargs={'session_key': self.client.session.session_key, 'input_array_id': self.test_array_id})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_single_kml(self):
        """ 
        Tests that single MPA can be represented as valid KML
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-mpa-kml', kwargs={'session_key': '0', 'input_mpa_id': self.test_mpa_id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

        # test session_key in url method
        url = reverse('kmlapp-mpa-kml', kwargs={'session_key': self.client.session.session_key, 'input_mpa_id': self.test_mpa_id})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 200)
        


    def test_user_kml_links(self):
        """
        Tests that user can retrieve valid KML file with network links to arrays
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-userlinks-kml', kwargs={'session_key': '0', 'input_username': self.user.username})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

        url = reverse('kmlapp-userlinks-kml', kwargs={'session_key': self.client.session.session_key, 'input_username': self.user.username})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 200)
            
    def test_public_kml_auth(self):
        """
        Tests that user can retrieve valid KML file for public shared mpas and arrays
        """
        # As authenticated user
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-publicshared-kml', kwargs={'session_key':self.client.session.session_key})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200, response)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_public_kml_unauth(self):
        """
        Tests that ANY user can retrieve valid KML file for public shared mpas and arrays
        """
        # As anonymous user
        url = reverse('kmlapp-publicshared-kml', kwargs={'session_key': '0'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_shared_kml(self):
        """ 
        Tests that another user can view the shared_kml (with network links the the sharedby-kmls)
        """
        self.client.login(username=self.user2.username, password=self.password)
        url = reverse('kmlapp-sharedlinks-kml', kwargs={'session_key':self.client.session.session_key, 'input_username':self.user2.username})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200, response)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_sharedby_kml(self):
        """
        Tests that user can view the sharedby_kml (mpas shared by a given group)
        """
        self.client.login(username=self.user2.username, password=self.password)
        url = reverse('kmlapp-sharedby-kml', kwargs={'session_key':self.client.session.session_key, 'input_shareuser': self.user.pk, 'input_sharegroup':self.group1.pk })
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200, response)
        errors = kml_errors(response.content)
        self.assertFalse(errors,"invalid KML %s" % str(errors))

    def test_kmz_view(self):
        """ 
        Tests that we can retrieve a zipped KML file (ie KMZ)
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-user-kmz', kwargs={'session_key': '0', 'input_username': self.user.username})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        url = reverse('kmlapp-user-kmz', kwargs={'session_key': self.client.session.session_key, 'input_username': self.user.username})
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 200)
        # once a user logs out, the session should be no good
        self.client.logout()
        response = self.other_client.get(url)
        self.assertEquals(response.status_code, 401)
        
    def test_nonexistant_mpa(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-mpa-kmz', kwargs={'session_key': self.client.session.session_key, 'input_mpa_id': '12345678910'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_nonexistant_array(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-array-kmz', kwargs={'session_key': self.client.session.session_key, 'input_array_id': '12345678910'})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_invalid_kml(self):
        """ 
        Tests that invalid KML gets noticed
        """
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('kmlapp-user-kml', kwargs={'session_key': 0, 'input_username': self.user.username})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        bad = str(response.content).replace("<Document>","<foobar /><Document>")
        errors = kml_errors(bad)
        self.assertEquals(errors[0][1]['element'],u'foobar')
