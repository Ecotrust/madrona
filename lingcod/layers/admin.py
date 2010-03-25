from django.contrib import admin
from lingcod.layers.models import PublicLayerList, UserLayerList


class UserLayerListAdmin(admin.ModelAdmin):
    pass
    

class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml', 'active', 'creation_date',)
    
admin.site.register(UserLayerList, UserLayerListAdmin)
admin.site.register(PublicLayerList, PublicLayerListAdmin)
