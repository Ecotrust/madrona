"""
Unit tests for the KML App
"""
from django.conf import settings
from django.test import TestCase
from django.contrib.gis.geos import GEOSGeometry 
from django.contrib.auth.models import *
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
Mpa = utils.get_mpa_class()
MpaArray = utils.get_array_class()

user = User.objects.get(username="dummy")

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


    def test_dummy_kml_view(self):
        """ 
        Tests that dummy user can retrieve a KML file 
        """
        response = self.client.get('/kml/dummy/mpa.kml', {})
        self.assertEquals(response.status_code, 200)

    def test_valid_kml(self):
        """ 
        Tests that dummy kml is valid (requires feedvalidator)
        """
        import feedvalidator
        from feedvalidator import compatibility

        response = self.client.get('/kml/dummy/mpa.kml', {})
        events = feedvalidator.validateString(response.content, firstOccurrenceOnly=1)['loggedEvents'] 

        # Three levels of compatibility
        # "A" is most basic level
        # "AA" mimics online validator
        # "AAA" is experimental; these rules WILL change or disappear in future versions
        filterFunc = getattr(compatibility, "AA")

        # there are a few bugs in feedvalidator, doesn't recognize valid ExtendedData element so we ignore
        events = [x for x in filterFunc(events) 
                 if not (isinstance(x,feedvalidator.logging.UndefinedElement) and x.params['element']==u'ExtendedData')]

        from feedvalidator.formatter.text_plain import Formatter
        output = Formatter(events)

        if output:
            print "\n".join(output)
            raise Exception("Invalid KML")
        else:
            print "No KML errors or warnings"

        self.assertEquals(response.status_code, 200)
