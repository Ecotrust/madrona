from django.contrib import admin
from econ_analysis.models import *

class FishingImpactAnalysisMapAdmin (admin.ModelAdmin):
    list_display = ('group_name', 'port_name', 'species_name')
    
class FishingImpactBaselineCostAdmin (admin.ModelAdmin):
    list_display = ('species', 'port', 'gross_revenue', 'crew', 'fuel', 'fixed', 'percentage_costs')
    
admin.site.register(FishingImpactAnalysisMap, FishingImpactAnalysisMapAdmin)
admin.site.register(FishingImpactBaselineCost, FishingImpactBaselineCostAdmin)
    

 