from django.contrib.gis.db import models
from lingcod.common import utils
from django.contrib.contenttypes.models import ContentType
from lingcod.sharing.managers import ShareableGeoManager

class ArrayManager(ShareableGeoManager):
    
    def empty(self):
        Mpa = utils.get_mpa_class()
        c = ContentType.objects.get_for_model(self.model)
        pks = Mpa.objects.filter(content_type=c).values_list('object_id', flat=True).distinct()
        return self.exclude(pk__in=pks)
