from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.xyquery.views',
        (r'^$', 'query' )
)
