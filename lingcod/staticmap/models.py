from django.contrib.gis.db import models

class MapConfig(models.Model):
    
    def __unicode__(self):
        return u"%s" % (self.mapfile)
    
    mapname = models.CharField(max_length=50,unique=True)
    mapfile = models.CharField(max_length=50)
    default_x1 = models.FloatField()
    default_y1 = models.FloatField()
    default_x2 = models.FloatField()
    default_y2 = models.FloatField()
    default_width = models.IntegerField()
    default_height = models.IntegerField()
