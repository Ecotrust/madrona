from django.contrib.gis import admin
from lingcod.straightline_spacing.models import *

class SpacingPointAdmin(admin.GeoModelAdmin):
    pass
admin.site.register(SpacingPoint,SpacingPointAdmin)