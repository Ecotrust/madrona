from django.conf.urls import url, include


urlpatterns = [
    (r'^$', madrona.studyregion.views.studyregion),
    url(r'^kml/$', 'madrona.studyregion.views.regionKml', name='studyregion-kml'),
    (r'^kml/(\d+)/$', 'madrona.studyregion.views.kml'),
    (r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', 'madrona.studyregion.views.regionKmlChunk'),
    (r'^lookAtKml/$', 'madrona.studyregion.views.regionLookAtKml'),
    (r'^show/(\d+)/$', madrona.studyregion.views.show),
]
