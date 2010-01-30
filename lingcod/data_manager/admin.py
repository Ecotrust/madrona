from django.contrib import admin
from lingcod.data_manager.models import *
from django.forms import TextInput, Textarea

class ShapefileInline(admin.TabularInline):
    #template = 'admin/edit_inline/modified_tabular.html'
    formfield_overrides = {
            models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':30})},
        }
    fieldsets = (
        (None,      {'fields': ('active','comment', ('update_display_layer','display_updated'),('update_analysis_layer','analysis_updated'),'shapefile')}),
    )
    # readonly_fields = ('field_description',)
    model = Shapefile
    sort = '-date_modified'
    #max_num = 2
    extra = 1

class ShapefileFieldInline(admin.TabularInline):
    model = ShapefileField
#    sort = sort
    extra = 0
    
class GeneralFileInline(admin.TabularInline):
    model = GeneralFile
    extra = 1
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'size':'15'})},
            models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':40})},
        }

class DataLayerAdmin(admin.ModelAdmin):
    list_display = ('name','date_modified')
    fieldsets = [
        (None,               {'fields': ('name',)}),
        ('Descriptive information', {'fields': ('description','metadata')}),
    ]
    inlines = [ShapefileInline, GeneralFileInline]
admin.site.register(DataLayer, DataLayerAdmin)

class ShapefileAdmin(admin.ModelAdmin):
    list_display = ('truncated_comment', 'data_layer', 'date_modified', 'date_created', 'update_display_layer', 'display_updated', 'update_analysis_layer', 'analysis_updated')
    list_filter = ('data_layer','update_display_layer','update_analysis_layer')
    search_fields = ('comment', )
    ordering = ['-date_modified']
    #inlines = [ShapefileFieldInline]
admin.site.register(Shapefile, ShapefileAdmin)

class GeneralFileAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_layer', 'date_modified', 'date_created',)
    list_filter = ('data_layer',)
    search_fields = ('description', 'name')
    ordering = ['-date_modified']
admin.site.register(GeneralFile, GeneralFileAdmin)