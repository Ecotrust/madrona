from django.contrib import admin
from madrona.screencasts.models import Screencast, YoutubeScreencast

class ScreencastAdmin(admin.ModelAdmin):
    pass

admin.site.register(Screencast)
admin.site.register(YoutubeScreencast)
