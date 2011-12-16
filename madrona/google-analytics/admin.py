from django.conf import settings
from django.contrib import admin
from django.contrib.sites.models import Site
from models import Analytics


if getattr(settings, 'GOOGLE_ANALYTICS_MODEL', False):
    class AnalyticsInline(admin.StackedInline):
        model = Analytics
        extra = 1
    class SiteAdminGA(admin.ModelAdmin):
        list_display = ('domain', 'name')
        model        = Site 
        inlines      = [AnalyticsInline]
    admin.site.unregister(Site)
    admin.site.register(Site, SiteAdminGA)
