from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.common.views',
    url(r'^/', 'map', name='map'),
)