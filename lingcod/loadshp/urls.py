from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.loadshp.views',
    url(r'^single/(?P<session_key>\w+)/', 'load_single_shp', name='loadshp-single'),
)
