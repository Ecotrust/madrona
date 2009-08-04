"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from lingcod.studyregion.models import StudyRegion
from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    (r'/studyregion/', include('lingcod.studyregion.urls')),
)


class StudyRegionTest(TestCase):

    def testStudyRegionPresent(self):
        """
        Check presence of test study region
        """
        self.assertEquals(StudyRegion.objects.count(), 1)
        self.assertEquals(StudyRegion.objects.all()[0].id, 1)
        
    def testComputeLookAt(self):
        """
        Check computing of lookat values
        """
        region = StudyRegion.objects.all()[0]
        region.lookAt_Lat = 0
        region.lookAt_Lon = 0
        self.assertEquals(region.lookAt_Lat, 0.0)
        self.assertEquals(region.lookAt_Lon, 0.0)
        lookat_kml = region.lookAtKml()
        self.assertEquals(round(region.lookAt_Lat, 9), 33.670316680)
        self.assertEquals(round(region.lookAt_Lon, 9), -118.995360206)
        
    def testLookAtView(self):
        """
        test views.regionLookAtKml
        """
        response = self.client.get('/studyregion/lookAtKml/', {})
        self.assertEqual(response.status_code, 200)
        
    def testKmlChunkView(self):
        """
        test views.kml_chunk
        """
        response = self.client.get('/studyregion/kml_chunk/34.473517/32.530798/-117.093325/-120.580374/', {})
        self.assertEqual(response.status_code, 200)
        
    def testKmlView(self):
        """
        test views.kml
        """
        response = self.client.get('/studyregion/kml/', {})
        self.assertEqual(response.status_code, 200)
        
    def testStudyRegionSandboxView(self):
        """
        test views.studyregion
        """
        response = self.client.get('/studyregion/', {})
        self.assertEqual(response.status_code, 200)


