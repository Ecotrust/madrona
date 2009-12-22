from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.kmlapp.views',
    # KMLs
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_mpa.kml$', 'create_kml', name='kmlapp-user-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_array_id>\d+)/array.kml$', 'create_kml', name='kmlapp-array-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_mpa_id>\d+)/mpa.kml$', 'create_kml', name='kmlapp-mpa-kml'),
    # KMZs
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_mpa.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-user-kmz'),
    url(r'^(?P<session_key>\w+)/(?P<input_array_id>\d+)/array.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-array-kmz'),
    url(r'^(?P<session_key>\w+)/(?P<input_mpa_id>\d+)/mpa.kmz$', 'create_kml', {'kmz': True}, name='kmlapp-mpa-kmz'),
    # KML/Zs with network links
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_mpa_links.kml$', 'create_kml', {'links': True}, name='kmlapp-userlinks-kml'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user_mpa_links.kmz$', 'create_kml', {'links': True, 'kmz': True}, name='kmlapp-userlinks-kmz')
)
