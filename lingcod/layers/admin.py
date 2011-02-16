from django.contrib import admin
from lingcod.layers.models import * 


class PrivateLayerListAdmin(admin.ModelAdmin):
    pass

class PrivateSuperOverlayAdmin(admin.ModelAdmin):
    pass

class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml', 'active', 'creation_date',)
    
admin.site.register(PublicLayerList, PublicLayerListAdmin)
admin.site.register(PrivateLayerList, PrivateLayerListAdmin)
admin.site.register(PrivateSuperOverlay, PrivateSuperOverlayAdmin)
