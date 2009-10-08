from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.simple.redirect_to', {'url':'/staticmap/default'} ),
)

urlpatterns += patterns('lingcod.staticmap.views',
    (r'^(?P<map_name>\w+)/$', 'show' )
)

