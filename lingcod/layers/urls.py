from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
)
