from lingcod.common.test_settings_manager import SettingsTestCase as TestCase
from lingcod.raster_stats.models import ZonalStatsCache, RasterDataset, zonal_stats, clear_cache
from django.contrib.gis.gdal.datasource import DataSource
from django.core import serializers
import os
import sys

def test_data():
    rastpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data/impact.tif')
    rast, created = RasterDataset.objects.get_or_create(name="test_impact",filepath=rastpath,type='continuous')  

    polygons = []

    shp = os.path.join(os.path.dirname(__file__), 'test_data/shapes.shp')
    ds = DataSource(shp)
    lyr = ds[0]
    assert len(lyr) == 4
    for feat in lyr:
        polygons.append(feat.geom.geos)

    del(lyr)
    del(ds)
    return rast, polygons

def test_categorical_data():
    rastpath = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_data/landuse.tif')
    rast, created = RasterDataset.objects.get_or_create(name="test_landuse",filepath=rastpath,type='categorical')  

    polygons = []

    shp = os.path.join(os.path.dirname(__file__), 'test_data/poly1.shp')
    ds = DataSource(shp)
    lyr = ds[0]
    for feat in lyr:
        polygons.append(feat.geom.geos)

    del(lyr)
    del(ds)
    return rast, polygons

class ZonalTest(TestCase):

    def setUp(self):
        clear_cache()
        self.rast, self.polygons = test_data()

    def test_zonal_util(self):
        """
        Tests that starspan works and stuff
        """
        # shouldnt have any nulls
        zonal = zonal_stats(self.polygons[0], self.rast)
        self.assertEqual(zonal.nulls,0)

        # doesnt even touch the raster, all should be null
        zonal = zonal_stats(self.polygons[1], self.rast)
        self.assertEqual(zonal.pixels,None)

        # Partly on and partly off the raster
        # no nulls but pixel count should be low
        zonal = zonal_stats(self.polygons[2], self.rast)
        self.assertEqual(zonal.nulls,0)
        self.assertEqual(zonal.pixels,225)

        # All on the raster but should have nulls
        zonal = zonal_stats(self.polygons[3], self.rast)
        self.assertEqual(zonal.nulls,279)

    def test_caching(self):
        """
        Test that the caching mechanism works and we can turn it on/off
        """
        clear_cache()
        self.assertEqual( len(ZonalStatsCache.objects.all()), 0)

        zonal = zonal_stats(self.polygons[0], self.rast)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(self.polygons[0], self.rast)
        self.assertEqual( zonal.from_cache, True)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(self.polygons[0], self.rast, read_cache=False)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(self.polygons[3], self.rast, write_cache=False)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(self.polygons[3], self.rast)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 2)

        zonal = zonal_stats(self.polygons[3], self.rast)
        self.assertEqual( zonal.from_cache, True)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 2)

        clear_cache()
        self.assertEqual( len(ZonalStatsCache.objects.all()), 0)

class ZonalWebServiceTest(TestCase):
    urls = 'lingcod.raster_stats.urls'

    def setUp(self):
        clear_cache()
        self.rast, self.polygons = test_data()

    def test_webservice(self):
        data = {'geom_txt': self.polygons[0].wkt}
        #self.settings_manager.set(ROOT_URLCONF = 'lingcod.raster_stats.urls')
        response = self.client.get('/test_impact/', data)
        self.failUnlessEqual(response.status_code, 200)

        for obj in serializers.deserialize("json", response.content):
            web_zonal = obj.object
            util_zonal = zonal_stats(self.polygons[0], self.rast, read_cache=False)
            self.failUnlessEqual(web_zonal.avg, util_zonal.avg)

class ZonalCategoriesTest(TestCase):
    def setUp(self):
        clear_cache()
        self.rast, self.polygons = test_categorical_data()

    def test_categories(self):
        zonal = zonal_stats(self.polygons[0], self.rast)
        sumpix = 0
        for zc in zonal.categories.all():
            sumpix += zc.count
        self.assertEqual(zonal.pixels, sumpix)

