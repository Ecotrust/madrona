from django.contrib import admin
from lingcod.layers.models import PublicLayerList


class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml', 'active', 'creation_date',)
    
admin.site.register(PublicLayerList, PublicLayerListAdmin)
