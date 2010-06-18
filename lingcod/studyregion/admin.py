from django.contrib.gis import admin
from lingcod.studyregion.models import StudyRegion


class StudyRegionAdmin(admin.GeoModelAdmin):
    list_display = ('name', 'active', 'creation_date', 'modification_date', )
    ordering = ('-active', '-creation_date', )
    fieldsets = (
        (None, {
            'fields': ('name', 'geometry')
        }),
        ('LookAt options', {
            'fields': ('lookAt_Lat', 'lookAt_Lon', 'lookAt_Range', 'lookAt_Tilt', 'lookAt_Heading', ), 
            'description': 'Change these if you want to manually define the default extent of the map.',
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('active',)
        }),
    )
    
admin.site.register(StudyRegion, StudyRegionAdmin)