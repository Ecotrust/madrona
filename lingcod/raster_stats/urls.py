from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.raster_stats.views',
    url(r'^$', 'raster_list', name="raster_list"),
    url(r'^(?P<raster_name>\w+)/$', 'stats_for_geom', name="raster_stats"),
)
