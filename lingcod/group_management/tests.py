"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.contrib.auth.models import Group, User
from lingcod.group_management.models import GroupRequest

class GroupManagementTest(TestCase):
    def test_group_request(self):
        """ 
        Tests that user can request membership with a group
        """
        user1 = User.objects.create_user('user1', 'test@marinemap.org', password='user1')
        group1 = Group.objects.create(name="Test Group 1")
        gr = GroupRequest(user=user1,group=group1)
        gr.save() 
        gr1 = GroupRequest.objects.all()
        self.assertEqual(len(gr1),1)
        self.assertEqual(gr1[0].user, user1)


