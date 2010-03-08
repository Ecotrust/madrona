from django.contrib import admin
from econ_analysis.models import *

class FishingImpactAnalysisMapAdmin (admin.ModelAdmin):
    list_display = ('group_name', 'port_name', 'species_name')
admin.site.register(FishingImpactAnalysisMap, FishingImpactAnalysisMapAdmin)

 