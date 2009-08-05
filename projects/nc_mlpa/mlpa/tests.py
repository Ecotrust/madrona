"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from mlpa.models import *
from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'/mlpa/', include('mlpa.urls')),
)


class MlpaTest(TestCase):
        
    def testKmlAllGeom(self):
        """
        test views.mpaKmlAllGeom
        """
        response = self.client.get('/mlpa/mpa/1/kmlAllGeom/', {})
        self.assertEquals(response.status_code, 200)
        
    def testKmlView(self):
        """
        test views.kml
        """
        response = self.client.get('/mlpa/mpa/1/kml/', {})
        self.assertEquals(response.status_code, 200)
        
    #def testExternalKmlStyle(self):
    #    response = self.client.get('/media/studyregion/styles.kml', {})
    #    self.assertEquals(response.status_code, 200)


