from django.contrib import admin
from lingcod.layers.models import PrivateLayerList, PublicLayerList, UserLayerList


class UserLayerListAdmin(admin.ModelAdmin):
    pass
    
class PrivateLayerListAdmin(admin.ModelAdmin):
    pass

class PublicLayerListAdmin(admin.ModelAdmin):
    list_display = ('kml', 'active', 'creation_date',)
    
admin.site.register(UserLayerList, UserLayerListAdmin)
admin.site.register(PublicLayerList, PublicLayerListAdmin)
admin.site.register(PrivateLayerList, PrivateLayerListAdmin)
