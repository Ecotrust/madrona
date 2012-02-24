from django.contrib import admin
from madrona.layers.models import * 

class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml_file', 'active', 'creation_date',)


class PrivateKmlAdmin(admin.ModelAdmin):
    pass

admin.site.register(PublicLayerList, PublicLayerListAdmin)
admin.site.register(PrivateKml, PrivateKmlAdmin)
