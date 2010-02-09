from django.contrib.gis import admin
from lingcod.mpa.models import Mpa, MpaDesignation

class MpaAdmin(admin.GeoModelAdmin):
    pass

class MpaDesignationAdmin(admin.ModelAdmin):
    list_display = ('acronym','name','sort')

admin.site.register(MpaDesignation, MpaDesignationAdmin)
