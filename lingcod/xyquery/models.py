import os
from django.contrib.gis.db import models
from django.conf import settings

class Layer(models.Model):
    name = models.CharField(max_length=50,unique=True)

    def __unicode__(self):
        return u"%s" % (self.name)

class Feature(models.Model):
    fid = models.AutoField(primary_key=True)
    layer = models.ForeignKey(Layer)
    geom = models.PolygonField(srid=4326)
    objects = models.GeoManager()

    def __unicode__(self):
        return u"Feature %d of layer %s" % (self.fid, self.layer)

class Attribute(models.Model):
    key = models.CharField(max_length=50)
    value = models.TextField()
    feature = models.ForeignKey(Feature)

    def __unicode__(self):
        return u"%s::%s" % (self.key,self.value)

rastdir = os.path.abspath(os.path.join(settings.MEDIA_ROOT, "xyquery_rasters"))
if not os.path.exists(rastdir):
    os.mkdir(rastdir)

class Raster(models.Model):
    layer = models.ForeignKey(Layer)
    filepath = models.FilePathField(path=rastdir, recursive=True)

    def __unicode__(self):
        return u"Raster layer %s" % (self.layer)
