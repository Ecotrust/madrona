from django.contrib import admin
from lingcod.screencasts.models import Screencast

class ScreencastAdmin(admin.ModelAdmin):
    pass

admin.site.register(Screencast)