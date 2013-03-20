from django.contrib import admin
from madrona.layer_manager.models import * 

class ThemeAdmin(admin.ModelAdmin):
    #list_display = ('name')
    pass


class LayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'layer_type', 'url', 'themes_string')

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(AttributeInfo)

