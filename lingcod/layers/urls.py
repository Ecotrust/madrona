from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
    url(r'^kml_file/(?P<session_key>\w+)/(?P<uid>[\w_]+).kml', 'get_kml_file', name='kml-file'),

    url(r'^overlay/(?P<pk>\d+)/(?P<session_key>\w+)/$', 'get_private_superoverlay', name='layers-superoverlay-private'),
    url(r'^overlay/(?P<pk>\d+)/(?P<session_key>\w+)/(?P<path>[^\z]+)$', 'get_relative_to_private_superoverlay', name='layers-relative'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
)
