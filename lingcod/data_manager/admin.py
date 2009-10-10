from django.contrib import admin
from lingcod.data_manager.models import *

class ShapefileInline(admin.StackedInline):
    template = 'admin/edit_inline/modified_tabular.html'
    model = Shapefile
#    sort = sort
    #max_num = 2
    extra = 1
    
class DataLayerAdmin(admin.ModelAdmin):
    list_display = ('name','date_modified')
    fieldsets = [
        (None,               {'fields': ('name',)}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    inlines = [ShapefileInline]
admin.site.register(DataLayer, DataLayerAdmin)

class ShapefileAdmin(admin.ModelAdmin):
    list_display = ('truncated_comment', 'data_layer', 'date_modified', 'update_display_layer', 'display_updated', 'update_analysis_layer', 'analysis_updated')
    list_filter = ('data_layer','update_display_layer','update_analysis_layer')
    search_fields = ('comment', )
    ordering = ['-date_modified']
admin.site.register(Shapefile, ShapefileAdmin)