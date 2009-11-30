"""
Unit tests for staticmap rendering via mapnik
"""

from django.test import TestCase, Client
from lingcod.staticmap.models import *
from django.conf.urls.defaults import *


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
   
    def testMpaFilter(self):
        """
        See if mapnik filter can render a select list of MPAs using the filter
        """
        response = self.client.get('/staticmap/default/?mpas=2,3,4', {})
        self.assertEquals(response.status_code, 200)
