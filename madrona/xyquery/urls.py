from django.conf.urls import *

urlpatterns = patterns('madrona.xyquery.views',
        (r'^$', 'query')
)
