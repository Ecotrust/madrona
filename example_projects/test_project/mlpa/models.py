from django.contrib.gis.db import models
from lingcod.features import register
from lingcod.features.models import PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.features.forms import FeatureForm

DESIGNATION_CHOICES = (
    ('R', 'Reserve'), 
    ('P', 'Park'),
    ('C', 'Conservation Area')
)

###########################
@register
class Mpa(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)
    class Options:
        verbose_name = 'Marine Protected Area'
        form = 'mlpa.models.MpaForm'
        manipulators = []
        
class MpaForm(FeatureForm):
    class Meta:
        model = Mpa

###########################
@register
class Array(FeatureCollection):
    class Options:
        form = 'mlpa.models.ArrayForm'
        valid_children = ( 'mlpa.models.Mpa', )

class ArrayForm(FeatureForm):
    class Meta:
        model = Array

###########################
@register
class Shipwreck(PointFeature):
    incident = models.CharField(max_length=100,default='')
    class Options:
        verbose_name = 'Shipwreck'
        form = 'mlpa.models.ShipwreckForm'

class ShipwreckForm(FeatureForm):
    class Meta:
        model = Shipwreck

###########################
@register
class Pipeline(LineFeature):
    type = models.CharField(max_length=30,default='')
    diameter = models.FloatField(null=True)
    class Options:
        verbose_name = 'Pipeline'
        form = 'mlpa.models.PipelineForm'

class PipelineForm(FeatureForm):
    class Meta:
        model = Pipeline

###########################
@register
class Folder(FeatureCollection):
    class Options:
        form = 'mlpa.models.FolderForm'
        valid_children = ( 
                'mlpa.models.Mpa', 
                'mlpa.models.Array', 
                'mlpa.models.Pipeline', 
                'mlpa.models.Shipwreck', 
                'mlpa.models.Folder' 
        )

class FolderForm(FeatureForm):
    class Meta:
        model = Folder

