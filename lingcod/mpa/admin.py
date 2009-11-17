from django.contrib.gis import admin
from lingcod.mpa.models import Mpa, MpaDesignation

class MpaAdmin(admin.GeoModelAdmin):
    pass

class MpaDesignationAdmin(admin.ModelAdmin):
    pass

admin.site.register(MpaDesignation, MpaDesignationAdmin)
