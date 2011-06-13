from django.contrib.gis.db import models
from lingcod.features import register
from lingcod.features.models import PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.layers.models import PrivateLayerList, PrivateSuperOverlay 
from lingcod.features.forms import FeatureForm, SpatialFeatureForm

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
        
class MpaForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = Mpa

###########################
@register
class Array(FeatureCollection):
    class Options:
        form = 'mlpa.models.ArrayForm'
        valid_children = ( 'mlpa.models.Mpa', )

class ArrayForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Array

###########################
@register
class Shipwreck(PointFeature):
    incident = models.CharField(max_length=100,default='')
    class Options:
        verbose_name = 'Shipwreck'
        form = 'mlpa.models.ShipwreckForm'

class ShipwreckForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = Shipwreck

###########################
@register
class Pipeline(LineFeature):
    type = models.CharField(max_length=30,default='')
    diameter = models.FloatField(null=True)
    class Options:
        verbose_name = 'Pipeline'
        form = 'mlpa.models.PipelineForm'

class PipelineForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
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
    class Meta(FeatureForm.Meta):
        model = Folder

###########################
@register
class UserKml(PrivateLayerList):
    class Options:
        form = 'mlpa.models.UserKmlForm'

class UserKmlForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = UserKml

