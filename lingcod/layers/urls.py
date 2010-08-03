from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),

    url(r'^private/networklinks/(?P<session_key>\w+)/', 'get_networklink_private_layers', name='private-data-layers'),
    url(r'^private/(?P<pk>\d+)/(?P<session_key>\w+)/', 'get_private_layer', name='layers-private'),
    url(r'^private/list/(?P<session_key>\w+)/', 'get_layerlist', name='layers-all-for-user'),

    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
)
