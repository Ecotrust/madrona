from django.contrib.gis.db import models

class MapConfig(models.Model):
    
    def __unicode__(self):
        return u"%s" % (self.mapfile)
    
    mapfile = models.CharField(max_length=50)
    #TODO make mapname unique pk
    mapname = models.CharField(max_length=50)
