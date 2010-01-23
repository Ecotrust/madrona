from django.contrib import admin
from mlpa.models import *
from lingcod.mpa.admin import MpaAdmin

class GoalObjectiveAdmin (admin.ModelAdmin):
    list_display = ( 'goal_category', 'name', 'description')
    list_filter = ['goal_category']
admin.site.register(GoalObjective, GoalObjectiveAdmin)

class GoalCategoryAdmin (admin.ModelAdmin):
    list_display = ('name', 'description')
admin.site.register(GoalCategory, GoalCategoryAdmin)

class AllowedUseAdmin (admin.ModelAdmin):
    list_display = ('target', 'method', 'purpose', 'lop', 'rule')
    list_filter = ['purpose', 'lop']
admin.site.register(AllowedUse, AllowedUseAdmin)
admin.site.register(AllowedMethod)
admin.site.register(AllowedPurpose)
admin.site.register(AllowedTarget)
admin.site.register(LopRule)
admin.site.register(DesignationsPurposes)
#admin.site.register(DomainHabitat)
admin.site.register(Lop)
# admin.site.register(HabitatsLinear, HabitatsLinearAdmin)
# admin.site.register(HabitatsAreal, HabitatsArealAdmin)
# class SatHabitatAdmin (admin.ModelAdmin):
#     list_display = ('name', 'type', 'sat_standard')
# admin.site.register(SatHabitat, SatHabitatAdmin)
class MpasAdmin (MpaAdmin):
    list_display = ( 'pk', 'name', 'user')
    list_filter = ['user','is_estuary']
admin.site.register(MlpaMpa, MpasAdmin)

from django.contrib.auth.models import Permission
admin.site.register(Permission)
admin.site.register(MpaArray)