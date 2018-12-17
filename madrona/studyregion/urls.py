from django.conf.urls import patterns, url, include


urlpatterns = patterns('madrona.studyregion.views',
    (r'^$', 'studyregion'),
    url(r'^kml/$', 'regionKml', name='studyregion-kml'),
    (r'^kml/(\d+)/$', 'kml'),
    (r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', 'regionKmlChunk'),
    (r'^lookAtKml/$', 'regionLookAtKml'),
    (r'^show/(\d+)/$', 'show'),
)
