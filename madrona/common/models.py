from django.contrib.gis.db import models

class KmlCache(models.Model):
    def __unicode__(self):
        return u"%s" % (self.key)
    key = models.CharField(max_length=250,unique=True, blank=False)
    kml_text = models.TextField(default='')
