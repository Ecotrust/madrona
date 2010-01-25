from django.contrib.gis import admin
from models import ShareableContent

class ShareableContentAdmin(admin.ModelAdmin):
    pass

admin.site.register(ShareableContent, ShareableContentAdmin)
