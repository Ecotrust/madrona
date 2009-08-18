"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase, Client
from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.gis.geos import GEOSGeometry, Polygon, Point, LinearRing
from lingcod.studyregion.models import StudyRegion

urlpatterns = patterns('',
    # Example:
    (r'/manipulators/', include('lingcod.manipulators.urls')),
)


class ManipulatorsTest(TestCase):

    def testManipulatorView(self):
        """
        test views.generic_manipulator_view
        """
        
        trans_geom = StudyRegion.objects.all()[0].geometry
        trans_geom.transform(4326)
        
        w = trans_geom.extent[0]
        s = trans_geom.extent[1]
        e = trans_geom.extent[2]
        n = trans_geom.extent[3]
        
        center_lat = trans_geom.centroid.y 
        center_lon = trans_geom.centroid.x
                
        target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))
        
         
        # test study region manipulator
        response = self.client.post('/manipulators/ClipToStudyRegion/', {'target_shape':target_shape.wkt, })
        self.assertEquals(response.status_code, 200)
        
        # test graticules
        response = self.client.post('/manipulators/ClipToGraticules/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"})
        self.assertEquals(response.status_code, 200)
        
        # test non-trivial multi manipulator case
        response = self.client.post('/manipulators/ClipToStudyRegion,ClipToGraticules/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
        # test reversed order of manipulators
        response = self.client.post('/manipulators/ClipToGraticules,ClipToStudyRegion/', {'target_shape':target_shape.wkt, "n":"40", "s":"30", "e":"-118", "w":"-119"}) 
        self.assertEquals(response.status_code, 200)
        
   