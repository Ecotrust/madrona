from django.contrib import admin
from madrona.layer_manager.models import * 
from django.forms import SelectMultiple

class ThemeAdmin(admin.ModelAdmin):
    #list_display = ('name')
    pass


class LayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'layer_type', 'url', 'themes_string')
    formfield_overrides = { models.ManyToManyField: {'widget': SelectMultiple(attrs={'size':'12'})}, }

admin.site.register(Theme, ThemeAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(AttributeInfo)
