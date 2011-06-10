from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
    url(r'^kml_file/(?P<session_key>\w+)/(?P<uid>[\w_]+).kml', 'get_kml_file', name='kml-file'),
    url(r'^privatekml/(?P<session_key>\w+)/$', 'get_privatekml_list', name='layers-privatekml-list'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/$', 'get_privatekml', name='layers-privatekml'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/(?P<path>[^\z]+)$', 'get_relative_to_privatekml', name='layers-privatekml-relative'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
)
