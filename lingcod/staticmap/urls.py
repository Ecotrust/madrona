from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.staticmap.views',
    (r'^$', 'staticmap' ),
)
