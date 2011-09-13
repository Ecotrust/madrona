from django.conf.urls.defaults import *
import time


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/$', 
        'get_public_layers', 
        name='public-data-layers'),

    # Useful for debugging, avoids GE caching interference
    url(r'^public/cachebuster/%s' % str(time.time()), 
        'get_public_layers', 
        name='public-data-layers-cachebuster'),

    url(r'^kml_file/(?P<session_key>\w+)/(?P<uid>[\w_]+).kml', 
        'get_kml_file', 
        name='kml-file'),
    url(r'^privatekml/(?P<session_key>\w+)/$', 
        'get_privatekml_list', 
        name='layers-privatekml-list'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/$', 
        'get_privatekml', 
        name='layers-privatekml'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/(?P<path>[^\z]+)$', 
        'get_relative_to_privatekml', 
        name='layers-privatekml-relative'),
)
