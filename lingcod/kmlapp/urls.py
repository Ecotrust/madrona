from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.kmlapp.views',
    # KMLs
    url(r'^(?P<input_username>\w+)/user_mpa.kml$', 'create_mpa_kml', name='user_mpa_kml' ),
    (r'^(?P<input_array_id>\d+)/array.kml$', 'create_mpa_kml' ),
    (r'^(?P<input_mpa_id>\d+)/mpa.kml$', 'create_mpa_kml' ),
    # KMZs
    url(r'^(?P<input_username>\w+)/user_mpa.kmz$', 'create_mpa_kmz', name='user_mpa_kmz' ),
    (r'^(?P<input_array_id>\d+)/array.kmz$', 'create_mpa_kmz' ),
    (r'^(?P<input_mpa_id>\d+)/mpa.kmz$', 'create_mpa_kmz' ),
    # KML/Zs with network links
    (r'^(?P<input_username>\w+)/user_mpa_links.kml$', 'create_mpa_kml_links' ),
    (r'^(?P<input_username>\w+)/user_mpa_links.kmz$', 'create_mpa_kmz_links' )
)
