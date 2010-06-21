import os
import sys
from django.test import TestCase
from django.contrib.gis.gdal.datasource import DataSource
from lingcod.raster_stats.models import ZonalStatsCache, RasterDataset, zonal_stats, clear_cache
from django.core import serializers


RASTER = os.path.join(os.path.dirname(__file__), 'test_data/impact.tif')
rast, created = RasterDataset.objects.get_or_create(name="test_impact",filepath=RASTER,type='continuous')  

POLYGONS = []

SHP = os.path.join(os.path.dirname(__file__), 'test_data/shapes.shp')
ds = DataSource(SHP)
lyr = ds[0]
assert len(lyr) == 4
for feat in lyr:
    POLYGONS.append(feat.geom.geos)

class ZonalTest(TestCase):
    def test_zonal_util(self):
        """
        Tests that starspan works and stuff
        """
        # shouldnt have any nulls
        zonal = zonal_stats(POLYGONS[0], rast)
        self.assertEqual(zonal.nulls,0)

        # doesnt even touch the raster, all should be null
        zonal = zonal_stats(POLYGONS[1], rast)
        self.assertEqual(zonal.pixels,None)

        # Partly on and partly off the raster
        # no nulls but pixel count should be low
        zonal = zonal_stats(POLYGONS[2], rast)
        self.assertEqual(zonal.nulls,0)
        self.assertEqual(zonal.pixels,225)

        # All on the raster but should have nulls
        zonal = zonal_stats(POLYGONS[3], rast)
        self.assertEqual(zonal.nulls,279)

    def test_caching(self):
        """
        Test that the caching mechanism works and we can turn it on/off
        """
        clear_cache()
        self.assertEqual( len(ZonalStatsCache.objects.all()), 0)

        zonal = zonal_stats(POLYGONS[0], rast)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(POLYGONS[0], rast)
        self.assertEqual( zonal.from_cache, True)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(POLYGONS[0], rast, read_cache=False)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(POLYGONS[3], rast, write_cache=False)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 1)

        zonal = zonal_stats(POLYGONS[3], rast)
        self.assertEqual( zonal.from_cache, False)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 2)

        zonal = zonal_stats(POLYGONS[3], rast)
        self.assertEqual( zonal.from_cache, True)
        self.assertEqual( len(ZonalStatsCache.objects.all()), 2)

        clear_cache()
        self.assertEqual( len(ZonalStatsCache.objects.all()), 0)

class ZonalWebServiceTest(TestCase):
    urls = 'lingcod.raster_stats.urls'

    def setUp(self):
        clear_cache()
        raster, created = RasterDataset.objects.get_or_create(name="test_impact",filepath=RASTER,type='continuous')  
        self.raster_pk  = rast.pk

    def test_webservice(self):
        data = {'geom_txt': POLYGONS[0].wkt}
        response = self.client.get('/%s/' % self.raster_pk, data)
        self.failUnlessEqual(response.status_code, 200)

        print response.content
        for obj in serializers.deserialize("json", response.content):
            web_zonal = obj.object
            util_zonal = zonal_stats(POLYGONS[0], rast, read_cache=False)
            self.failUnlessEqual(web_zonal.avg, util_zonal.avg)
