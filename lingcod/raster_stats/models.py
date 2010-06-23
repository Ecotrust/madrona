from django.db import models
from django.conf import settings
from django.core import serializers
import tempfile
import os

verbose = False
RASTDIR = os.path.join(os.path.dirname(__file__), 'test_data')
RASTER_TYPES = ( 
                ("continuous", "continuous"),
                ("categorical", "catgorical"),
               )
try:
    STARSPAN_BIN = settings.STARSPAN_BIN
except:
    STARSPAN_BIN = 'starspan'


class RasterDataset(models.Model):
    name = models.CharField(max_length=30, unique=True)
    filepath = models.FilePathField(path=RASTDIR, recursive=True)
    type = models.CharField(max_length=30, choices=RASTER_TYPES)
    
    def __unicode__(self):
        return unicode(self.name + " raster at " + self.filepath)
    
class ZonalStatsCache(models.Model):
    geom_hash = models.CharField(max_length=255)
    raster = models.ForeignKey('RasterDataset')
    avg = models.FloatField(null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    max = models.FloatField(null=True, blank=True)
    mode = models.FloatField(null=True, blank=True)
    median = models.FloatField(null=True, blank=True)
    stdev = models.FloatField(null=True, blank=True)
    nulls = models.FloatField(null=True, blank=True)
    pixels = models.FloatField(null=True, blank=True)
    date_modified = models.DateTimeField(auto_now=True)

    @property
    def json(self):
        return serializers.serialize("json", self)

    def __unicode__(self):
        return unicode("Zonal Stats - avg:%s , min:%s, max:%s" % (self.avg, self.min, self.max))

    class Meta:
        unique_together = ('geom_hash', 'raster')

def geom_to_file(geom, filepath):
    json = """{
"type": "FeatureCollection",
"features": [
{ "type": "Feature", "properties": { "id": 1 }, "geometry": %s }
]
}""" % geom.json
    fh = open(filepath,'w')
    fh.write(json)
    fh.close()
    assert os.path.exists(filepath)

def run_starspan_zonal(geom, rasterds, write_cache=False):
    """
    Consider this a 'private' method .. dont call directly, use zonal_stats() instead
    Runs starspan and returns a ZonalStatsCache object
    If not write_cache, just return an unsaved object
    """
    # Create tempdir and cd in 
    tmpdir = tempfile.gettempdir()
    os.chdir(tmpdir)

    # Output geom to temp dataset
    out_json = os.path.join(tmpdir, 'geom.json')
    geom_to_file(geom, out_json)

    # Run starspan
    out_csv = os.path.join(tmpdir, 'output_stats.csv')
    if os.path.exists(out_csv):
        os.remove(out_csv)
    cmd = '%s --vector %s --where "id=1" --out-prefix %s/output --out-type table --summary-suffix _stats.csv --raster %s --stats avg mode median min max sum stdev nulls ' % (STARSPAN_BIN,out_json,tmpdir, rasterds.filepath)
    if verbose: print cmd
    starspan_out = os.popen(cmd).read()
    if verbose: print starspan_out

    # Parse output
    try:
        res = open(out_csv,'r').readlines()
    except IOError:
        print "Starspan failed to create output csv properly"
        raise Exception
    if verbose: print res

    # Create zonal model
    hash = geom.wkt.__hash__()
    zonal = ZonalStatsCache(raster=rasterds, geom_hash=hash)

    # Make sure we have valid results output by starspan
    if len(res) == 2 and "Intersecting features: 0" not in starspan_out:
        headers = [x.strip() for x in res[0].split(',')]
        vals = [x.strip() for x in res[1].split(',')]
        assert len(headers) == len(vals)

        # loop and populate model
        for i in range(len(headers)):
            if "_Band1" in headers[i]:
                stat_type = headers[i].replace("_Band1",'')
                zonal.__dict__[stat_type] = float(vals[i])
            elif headers[i] == 'numPixels':
                zonal.pixels = float(vals[i])

    # return zonal object (caching it if needed)
    if write_cache:
        zonal.save()
    return zonal

def clear_cache():
    objs = ZonalStatsCache.objects.all()
    if verbose: print "Clearing %s objects from cache" % len(objs)
    objs.delete()

def zonal_stats(geom, rasterds, write_cache=True, read_cache=True):
    """
    Given a GEOSGeometry and a RasterDataset,
    compute the zonal stats and return json like
     { 'raster': 'elevation', 'stats': {'sum': 10234.2, 'mean': 12.4}}
    result can be stored in cache (write_cache)
     and cache value is returned if read_cache
    """
    if not geom.valid:
        return None

    hash = geom.wkt.__hash__()
     
    cached = None
    if read_cache:
        try:
            cached = ZonalStatsCache.objects.get(geom_hash=hash, raster=rasterds)
        except ZonalStatsCache.DoesNotExist:
            cached = None
    else:
        write_cache = False #If we're not reading the cache, we're not going to write to it either

    if cached:
        result = cached
        result.from_cache = True
    else:
        result = run_starspan_zonal(geom, rasterds, write_cache=write_cache)
        result.from_cache = False
    
    return result
