from lingcod.mpa.admin import MpaAdmin
from lingcod.array.admin import ArrayAdmin
from django.contrib.gis import admin
from simple_app.models import Mpa, MpaArray

admin.site.register(Mpa, MpaAdmin)
admin.site.register(MpaArray, ArrayAdmin)
