from django.conf.urls.defaults import *
from lingcod.spacing.views import *

urlpatterns = patterns('',
    # Example:
    (r'^$', Index),
    url(r'^land/kml/', LandKML, name='land_kml'),
    url(r'^fish_distance/kml', FishDistanceKML, name='fish_distance_kml'),
    url(r'^spacing_points/kml/', SpacingPointKML, name='spacing_point_kml'),
    url(r'^spacing_network/kml/', SpacingNetworkKML, name='spacing_network_kml'),
)