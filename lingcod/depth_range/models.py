from django.contrib.gis.db import models
from django.conf import settings
from django.db.models import Max,Min


# Create your models here.
class DepthSounding(models.Model):
    depth_ft = models.IntegerField(blank=True,null=True)
    geometry = models.PointField(srid=settings.GEOMETRY_DB_SRID)
    objects = models.GeoManager()
    
    def __unicode__(self):
        return self.depth_ft
    
def soundings_in_geom(geom):
    """
    Return a query set of depthsoundings that fall within the supplied geometry.
    """
    return DepthSounding.objects.filter(geometry__within=geom)
    
def depth_range(geom):
    """
    Return the Minimum and Maximum depth range for a geometry.  If the minimum is less than
    10 ft., return 0 as the min.
    Always return positive numbers.
    """
    ds = soundings_in_geom(geom)
    ds_min = ds.aggregate(Min('depth_ft'))['depth_ft__min']
    ds_max = ds.aggregate(Max('depth_ft'))['depth_ft__max']
    # Account for the fact that soundings may be negative or positive
    if ds_min and ds_max: 
        shallowest_positive = min([abs(ds_min),abs(ds_max)])
        deepest_positive = max([abs(ds_min),abs(ds_max)])
    else:
        shallowest_positive = None
        deepest_positive = None
    if shallowest_positive and shallowest_positive < 10:
        shallowest_positive = 0
    return shallowest_positive, deepest_positive
    
