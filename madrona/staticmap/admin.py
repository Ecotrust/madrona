from django.contrib import admin
from madrona.staticmap.models import MapConfig

class MapAdmin(admin.ModelAdmin):
    pass

admin.site.register(MapConfig, MapAdmin)
