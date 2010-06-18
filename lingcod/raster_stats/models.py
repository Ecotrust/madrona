from django.db import models

RASTDIR = '/Users/perry/src/marinemap/lingcod/raster_stats/test_data'
RASTER_TYPES = ("continuous","catgorical")

class RasterDataset:
    name = models.CharField(max_length=30, unique=True)
    filepath = models.FilePathField(path=RASTDIR, recursive=True)
    type = models.CharField(max_length=30, choices=RASTER_TYPES)
    
class ZonalStats:
    geom_hash = models.CharField(max_length=255)
    raster = models.ForeignKey(RasterDataset)
    avg = model.FloatField()
    min = model.FloatField()
    max = model.FloatField()
    mode = model.FloatField()
    stdev = model.FloatField()
    nulls = model.FloatField()
    pixels = model.FloatField()
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('geom_hash', 'raster')
