from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/user/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/user/', 'get_user_layers', name='user-data-layers'),
    #url(r'^user/', 'get_user_layers', name='user-data-layers'),
)
