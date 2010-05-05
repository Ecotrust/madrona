from django.contrib.gis import admin
from lingcod.replication.models import *

class HabitatThresholdInline(admin.TabularInline):
    model = HabitatThreshold
    # readonly_fields = ['habitat','units']
    fields = ['habitat','minimum_quantity','units','rule']
    sort = ['habitat__sort']
    extra = 0
    
class ReplicationSetupAdmin(admin.ModelAdmin):
    inlines = [HabitatThresholdInline]
    
admin.site.register(ReplicationSetup, ReplicationSetupAdmin)

class ThresholdRuleAdmin(admin.ModelAdmin):
    readonly_fields = ['description']
admin.site.register(ThresholdRule, ThresholdRuleAdmin)