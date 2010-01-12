from django.contrib.gis import admin
from lingcod.data_distributor.views import run_load_setup
from lingcod.data_distributor.models import *

# def load_potential_targets(modeladmin, request, queryset):
#     load_potential_targets(module='lingcod')
# load_potential_targets.short_description = 'Load all lingcod app models to Potential Targets'

def run_load_setups(modeladmin, request, queryset):
    for lsu in queryset:
        run_load_setup(request, lsu.pk)
run_load_setups.short_description = 'Run the selected Load Setups'

class PotentialTargetsAdmin(admin.ModelAdmin):
    list_display = ('name','module_text')
    #actions = [load_potential_targets]
    
admin.site.register(PotentialTarget,PotentialTargetsAdmin)

class LoadSetupAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ('name','origin_data_layer','target_model','geometry_only')}),
        ('Field Setup',      {'fields': ('origin_field_choices','origin_field','target_field_choices','target_field')}),
    ]
    actions = [run_load_setups]
    
admin.site.register(LoadSetup,LoadSetupAdmin)