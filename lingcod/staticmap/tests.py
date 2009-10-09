"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from lingcod.staticmap.models import *
from django.conf import settings
from django.conf.urls.defaults import *

#urlpatterns = patterns('',
# Example:
#    (r'/staticmap/', include('lingcod.staticmap.urls')),
#)


class StaticMapTest(TestCase):

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
        
    def testRedirectDefault(self):
        """
        test the redirection of staticmap without map name specified
        """
        response = self.client.get('/staticmap/', {})
        self.assertEquals(response.status_code, 301)

   
