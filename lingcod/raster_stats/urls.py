from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.raster_stats.views',
    url(r'^(?P<pk>\d+)/$', 'stats_for_geom', name="raster_stats"),
)
