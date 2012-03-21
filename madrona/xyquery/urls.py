from django.conf.urls.defaults import *

urlpatterns = patterns('madrona.xyquery.views',
        (r'^$', 'query')
)
