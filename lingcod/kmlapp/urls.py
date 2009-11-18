from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.kmlapp.views',
    (r'^(?P<input_username>\w+)/mpa.kml$', 'create_mpa_kml' ),
    (r'^(?P<input_username>\w+)/mpa.kmz$', 'create_mpa_kmz' )
)
