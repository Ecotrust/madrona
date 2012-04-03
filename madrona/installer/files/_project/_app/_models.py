from django.db import models
from madrona.features import register
from madrona.features.models import PolygonFeature, FeatureCollection

################## EXAMPLE ###########################################
@register
class AOI(PolygonFeature):
    class Options:
        form = '_app.forms.AOIForm'

@register
class Folder(FeatureCollection):
    class Options:
        form = '_app.forms.FolderForm'
        valid_children = (
            '_app.models.AOI',
            '_app.models.Folder',
        )
################## END EXAMPLE #######################################
