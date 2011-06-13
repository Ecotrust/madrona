from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.staticmap.views',
    url(r'^(?P<map_name>\w+)/$', 'show',name="staticmap-show" ),
    url(r'^(?P<map_name>\w+)/$', 'staticmap_link',name="staticmap-link" ),
    (r'^$', 'show' )
)
