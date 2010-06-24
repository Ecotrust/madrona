from django.contrib.gis import admin
from lingcod.raster_stats.models import RasterDataset, ZonalStatsCache

admin.site.register(RasterDataset)
admin.site.register(ZonalStatsCache)
