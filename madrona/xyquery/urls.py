from django.conf.urls import patterns, url, include

urlpatterns = patterns('madrona.xyquery.views',
        (r'^$', 'query')
)
