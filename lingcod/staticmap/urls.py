from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse

urlpatterns = patterns('lingcod.staticmap.views',
    (r'^(?P<map_name>\w+)/$', 'show' ),
    (r'^$', 'show' )
)
