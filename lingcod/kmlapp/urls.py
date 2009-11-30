from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.kmlapp.views',
    (r'^(?P<input_username>\w+)/user_mpa.kml$', 'create_mpa_kml' ),
    (r'^(?P<input_array_id>\d+)/array.kml$', 'create_mpa_kml' ),
    (r'^(?P<input_mpa_id>\d+)/mpa.kml$', 'create_mpa_kml' ),
    (r'^(?P<input_username>\w+)/user_mpa.kmz$', 'create_mpa_kmz' )
)
