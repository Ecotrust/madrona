from django.contrib import admin
from econ_analysis.models import *

class FishingImpactAnalysisMapAdmin (admin.ModelAdmin):
    list_display = ('group_name', 'port_name', 'species_name')
        
class  CommercialSpeciesAdmin (admin.ModelAdmin):
    list_display = ('name',)
    
class  CommercialPortAdmin (admin.ModelAdmin):
    list_display = ('name',)
    
class CommercialCostsAdmin (admin.ModelAdmin):
    list_display = ('species', 'crew', 'fuel', 'fixed', 'percentage_costs')
    
class CommercialGrossRevenueAdmin (admin.ModelAdmin):
    list_display = ('species', 'port', 'gross_revenue')
        
class CPFVPortAdmin (admin.ModelAdmin):
    list_display = ('name',)
    
class CPFVCostsAdmin (admin.ModelAdmin):
    list_display = ('port', 'crew', 'fuel', 'fixed', 'percentage_costs')
    
class CPFVGrossRevenueAdmin (admin.ModelAdmin):
    list_display = ('port', 'gross_revenue')
    
admin.site.register(FishingImpactAnalysisMap, FishingImpactAnalysisMapAdmin)

admin.site.register(CommercialSpecies, CommercialSpeciesAdmin)
admin.site.register(CommercialPort, CommercialPortAdmin)
admin.site.register(CommercialCosts, CommercialCostsAdmin)
admin.site.register(CommercialGrossRevenue, CommercialGrossRevenueAdmin)

admin.site.register(CPFVPort, CPFVPortAdmin)
admin.site.register(CPFVCosts, CPFVCostsAdmin)
admin.site.register(CPFVGrossRevenue, CPFVGrossRevenueAdmin)    

 