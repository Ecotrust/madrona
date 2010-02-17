from lingcod.common.test_settings_manager import SettingsTestCase as TestCase
from lingcod.array.models import MpaArray
from lingcod.mpa.models import Mpa, MpaDesignation
from lingcod.common import utils 
from lingcod.sharing.models import * 
from lingcod.sharing.utils import can_user_view
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.gis.db import models
from django.contrib.gis.geos import GEOSGeometry 

class SharingTestMpa(Mpa):
    extra_attr = models.CharField(max_length=255, blank=True)

class SharingTestArray(MpaArray):
    extra_attr = models.CharField(max_length=255, blank=True)

settings.MPA_CLASS = 'lingcod.sharing.tests.SharingTestMpa'
settings.ARRAY_CLASS = 'lingcod.sharing.tests.SharingTestArray'

class SharingTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # First register the mpas and arrays as shareable content types
        mpa_ct = ContentType.objects.get(app_label='sharing',model='sharingtestmpa')
        array_ct = ContentType.objects.get(app_label='sharing',model='sharingtestarray')

        share_mpa = ShareableContent.objects.create(shared_content_type=mpa_ct, 
                                                    container_content_type=array_ct,
                                                    container_set_property='mpa_set')
        share_array = ShareableContent.objects.create(shared_content_type=array_ct)

        # Create 3 users
        self.password = 'iluvsharing'
        self.user1 = User.objects.create_user('user1', 'test@marinemap.org', password=self.password)
        self.user2 = User.objects.create_user('user2', 'test@marinemap.org', password=self.password)
        self.user3 = User.objects.create_user('user3', 'test@marinemap.org', password=self.password)

        # Create some groups
        # Group 1 has user1 and user2 and can share
        # Group 2 has user2 and user3 and has no sharing permissions
        group1 = Group.objects.create(name="Test Group 1")
        group1.save()
        self.group1_id = group1.id
        self.user1.groups.add(group1)
        self.user2.groups.add(group1)

        group2 = Group.objects.create(name="Test Group 2")
        group2.save()
        self.group2_id = group2.id
        self.user2.groups.add(group2)
        self.user3.groups.add(group2)

        shareables = get_shareables()
        for modelname in shareables.iterkeys():
            group1.permissions.add(shareables[modelname][1])
        
        # Create some necessary objects
        g1 = GEOSGeometry('SRID=4326;POLYGON ((-120.42 34.37, -119.64 34.32, -119.63 34.12, -120.44 34.15, -120.42 34.37))')
        g1.transform(settings.GEOMETRY_DB_SRID)

        smr = MpaDesignation.objects.create(name="Reserve of some sort", acronym="R")
        smr.save()

        # Create three Mpas by different users
        mpa1 = SharingTestMpa.objects.create( name='Test_MPA_1', designation=smr, user=self.user1, geometry_final=g1)
        mpa1.save()
        self.mpa1_id = mpa1.id

        mpa2 = SharingTestMpa.objects.create( name='Test_MPA_2', designation=smr, user=self.user2, geometry_final=g1)
        mpa2.save()
        self.mpa2_id = mpa2.id

        mpa3 = SharingTestMpa.objects.create( name='Test_MPA_3', designation=smr, user=self.user3, geometry_final=g1)
        mpa3.save()
        self.mpa3_id = mpa3.id

        # User1 adds mpa to an array
        array1 = SharingTestArray.objects.create( name='Test_Array_1', user=self.user1)
        array1.save()
        mpa1.add_to_array(array1)
        self.array1_id = array1.id

    def test_nothing_shared(self):
        """
        Make sure nothing is shared yet
        """
        shared_mpas = SharingTestMpa.objects.shared_with_user(self.user1)
        self.assertEquals(len(shared_mpas),0)

    def test_share_mpa(self):
        """
        Make sure the basic sharing of mpas works
        """
        # User2 shares their MPA2 with Group1
        mpa2 = SharingTestMpa.objects.get(id=self.mpa2_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(mpa2, group1) 
        # User1 should see it (since they're part of Group1)
        shared_mpas = SharingTestMpa.objects.shared_with_user(self.user1)
        self.assertEquals(len(shared_mpas),1)
        # User3 should not see it since they're not part of Group1
        shared_mpas = SharingTestMpa.objects.shared_with_user(self.user3)
        self.assertEquals(len(shared_mpas),0)

    def test_share_mpa_shortcut(self):
        """
        Make sure the basic sharing of mpas works using the can_user_view shortcut
        """
        # User2 shares their MPA2 with Group1
        mpa2 = SharingTestMpa.objects.get(id=self.mpa2_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(mpa2, group1) 
        # User 2 should be able to view it since they own it
        viewable, response = can_user_view(SharingTestMpa, self.mpa2_id, self.user2)
        self.assertEquals( viewable, True )
        # User1 should see it (since they're part of Group1)
        viewable, response = can_user_view(SharingTestMpa, self.mpa2_id, self.user1)
        self.assertEquals( viewable, True )
        # User3 should not see it since they're not part of Group1
        viewable, response = can_user_view(SharingTestMpa, self.mpa2_id, self.user3)
        self.assertEquals( viewable, False )

    def test_share_with_bad_group(self):
        """
        Make sure we can't share with a group which does not have permissions
        """
        # User2 trys to share their MPA2 with Group2
        mpa2 = SharingTestMpa.objects.get(id=self.mpa2_id)
        group2 = Group.objects.get(id=self.group2_id)
        # Would use assertRaises here but can't figure how to pass args to callable
        # see http://www.mail-archive.com/django-users@googlegroups.com/msg46609.html
        error_occured = False
        try:
            share_object_with_group(mpa2, group2) 
        except SharingError:
            error_occured = True
        self.assertTrue(error_occured)

    def test_share_by_bad_user(self):
        """
        Make sure user without permissions can't share their objects
        """
        # User3 trys to share their MPA3 with Group1
        mpa3 = SharingTestMpa.objects.get(id=self.mpa3_id)
        group1 = Group.objects.get(id=self.group1_id)
        error_occured = False
        try:
            share_object_with_group(mpa3, group1) 
        except SharingError:
            error_occured = True
        self.assertTrue(error_occured)

    def test_share_arrays(self):
        """
        Make sure the basic sharing of arrays works
        """
        # User1 shares their array1 with Group1
        array1 = SharingTestArray.objects.get(id=self.array1_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(array1, group1) 
        # User2 should see it (since they're part of Group1)
        shared_mpas = SharingTestArray.objects.shared_with_user(self.user2)
        self.assertEquals(len(shared_mpas),1)
        # User3 should not see it (since they're not part of Group1)
        shared_mpas = SharingTestArray.objects.shared_with_user(self.user3)
        self.assertEquals(len(shared_mpas),0)

    def test_share_container(self):
        """
        Arrays are containers of MPAs so their child objects should also appear to be shared
        """
        # User1 shares their array1 (which contains MPA1) with Group1
        array1 = SharingTestArray.objects.get(id=self.array1_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(array1, group1) 
        # User2 should see the mpa contained in array1 (since they're part of Group1)
        shared_mpas = SharingTestMpa.objects.shared_with_user(self.user2)
        self.assertEquals(len(shared_mpas),1)
        # User3 should not see it (since they're not part of Group1)
        shared_mpas = SharingTestMpa.objects.shared_with_user(self.user3)
        self.assertEquals(len(shared_mpas),0)

    def test_share_container_shortcut(self):
        """
        Arrays are containers of MPAs so their child objects should also appear to be shared
        Uses the can_user_view shortcut
        """
        # User1 shares their array1 (which contains MPA1) with Group1
        array1 = SharingTestArray.objects.get(id=self.array1_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(array1, group1) 
        # User 1 should see it since they own it
        viewable, response = can_user_view(SharingTestMpa, self.mpa1_id, self.user1)
        self.assertEquals( viewable, True )
        # User2 should see the mpa contained in array1 (since they're part of Group1)
        viewable, response = can_user_view(SharingTestMpa, self.mpa1_id, self.user2)
        self.assertEquals( viewable, True )
        # User3 should not see it (since they're not part of Group1)
        viewable, response = can_user_view(SharingTestMpa, self.mpa1_id, self.user3)
        self.assertEquals( viewable, False )

    def test_share_unshareable(self):
        """
        Test how the app will react to sharing arbitrary unsharable objects
        """
        group1 = Group.objects.get(id=self.group1_id)
        # Groups obvioulsy cant be shared objects since they are the entity we are sharing *with*
        # so we can safely use that as an example
        unshareable_thing = Group.objects.get(id=self.group2_id)
        error_occured = False
        try:
            share_object_with_group(unshareable_thing, group1) 
        except SharingError:
            error_occured = True
        self.assertTrue(error_occured)

    def test_groups_users_sharing_with(self):
        """
        Test if we can get a list of groups and users who are sharing with a given user
        """
        # User1 shares their array1 (which contains MPA1) with Group1
        array1 = SharingTestArray.objects.get(id=self.array1_id)
        group1 = Group.objects.get(id=self.group1_id)
        share_object_with_group(array1, group1) 
        # User1 should NOT see himself 
        sw = groups_users_sharing_with(self.user1)
        self.assertEquals(sw,None)
        # User2 should see group1:user1 as a sharer
        sw = groups_users_sharing_with(self.user2)
        usernames = [x.username for x in sw['Test Group 1']['users']]
        self.assertEquals(usernames, ['user1'])
        # User3 should see nothing
        sw = groups_users_sharing_with(self.user3)
        self.assertEquals(sw, None)
