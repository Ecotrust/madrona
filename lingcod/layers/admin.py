from django.contrib import admin
from lingcod.layers.models import * 

class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml_file', 'active', 'creation_date',)
    
admin.site.register(PublicLayerList, PublicLayerListAdmin)
