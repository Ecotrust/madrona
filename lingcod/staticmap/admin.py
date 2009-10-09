from django.contrib import admin
from lingcod.staticmap.models import MapConfig

class MapAdmin(admin.ModelAdmin):
    pass

admin.site.register(MapConfig, MapAdmin)

