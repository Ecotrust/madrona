from django.db import models
from madrona.features import register

################## EXAMPLE ###########################################
#from madrona.features.models import PolygonFeature, FeatureCollection
#
#@register
#class AOI(PolygonFeature):
#    class Options:
#        form = '_project._app.forms.AOIForm'
#
#@register
#class Folder(FeatureCollection):
#    class Options:
#        form = '_project._app.forms.FolderForm'
#        valid_children = (
#            '_project._app.models.AOI',
#            '_project._app.models.Folder',
#        )
################## END EXAMPLE #######################################
