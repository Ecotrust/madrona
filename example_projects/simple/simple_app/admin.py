from lingcod.mpa.admin import MpaAdmin
from django.contrib.gis import admin
from simple_app.models import Mpa

admin.site.register(Mpa, MpaAdmin)
