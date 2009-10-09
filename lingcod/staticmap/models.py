from django.contrib.gis.db import models

class MapConfig(models.Model):
    
    def __unicode__(self):
        return u"%s" % (self.mapfile)
    
    mapname = models.CharField(max_length=50,unique=True)
    mapfile = models.FileField(upload_to='staticmap/', help_text="""
        Mapnik xml configuration file that defines data sources and styles. 
        All paths within xml must be relative to media/staticmap/
    """, blank=False, max_length=510)
    default_x1 = models.FloatField()
    default_y1 = models.FloatField()
    default_x2 = models.FloatField()
    default_y2 = models.FloatField()
    default_width = models.IntegerField()
    default_height = models.IntegerField()
