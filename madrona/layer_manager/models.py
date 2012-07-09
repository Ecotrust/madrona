from django.db import models

class Theme(models.Model):
    name = models.CharField(max_length=100)
    layer = models.ManyToManyField('Layer', related_name='layer', blank=True, null=True)

    class Meta:
        db_table = u'theme'
    def __unicode__(self):
        return unicode('%s' % (self.name))

    @property
    def toDict(self):
        layers = [layer.id for layer in self.layer.all()]
        themes_dict = {
            'name': self.name,
            'layers': layers,
        }
        return themes_dict

class Layer(models.Model):
    TYPE_CHOICES = (
        ('XYZ', 'XYZ'),
        ('WMS', 'WMS'),
        ('radio', 'radio'),
    )
    name = models.CharField(max_length=100)
    layer_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    url = models.CharField(max_length=255, blank=True, null=True)
    sublayer = models.ManyToManyField('self', blank=True, null=True)
    theme = models.ManyToManyField(Theme, related_name='theme', blank=True, null=True)
    is_sublayer = models.BooleanField(default=False)
    legend = models.CharField(max_length=255, blank=True, null=True)
    utfurl = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = u'layer'
    def __unicode__(self):
        return unicode('%s' % (self.name))

    @property
    def toDict(self):
        sublayers = [{
	    'name': layer.name,
            'type': layer.layer_type,
            'url': layer.url,
	    'utfurl': layer.utfurl,
            'id': layer.id,
	    'parent': self.id,
	    'legend': layer.legend 
	} for layer in self.sublayer.all()]
        layers_dict = {
            'name': self.name,
            'type': self.layer_type,
            'url': self.url,
	    'utfurl': self.utfurl,
            'subLayers': sublayers,
            'legend': self.legend,
            'id': self.id
        }
        return layers_dict
