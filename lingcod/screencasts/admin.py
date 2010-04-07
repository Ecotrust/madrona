from django.contrib import admin
from lingcod.screencasts.models import Screencast, YoutubeScreencast

class ScreencastAdmin(admin.ModelAdmin):
    pass

admin.site.register(Screencast)
admin.site.register(YoutubeScreencast)
