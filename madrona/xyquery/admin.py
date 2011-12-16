from django.contrib.gis import admin
from models import Layer, Feature, Attribute, Raster

class LayerAdmin(admin.ModelAdmin):
    pass

class FeatureAdmin(admin.GeoModelAdmin):
    pass

class AttributeAdmin(admin.ModelAdmin):
    pass

class RasterAdmin(admin.ModelAdmin):
    pass

admin.site.register(Raster, RasterAdmin)
admin.site.register(Layer, LayerAdmin)
admin.site.register(Feature, FeatureAdmin)
admin.site.register(Attribute, AttributeAdmin)

