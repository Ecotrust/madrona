from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user/', 'get_user_layers', name='user-data-layers'),
    url(r'^private/(?P<pk>\d+)/(?P<session_key>\w+)/', 'get_private_layer', name='layers-private'),
    url(r'^private/all/(?P<session_key>\w+)/', 'get_layers_for_user', name='layers-all-for-user'),
    #url(r'^user/', 'get_user_layers', name='user-data-layers'),
)
