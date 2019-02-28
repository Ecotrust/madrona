from django.conf.urls import url, include
from madrona.studyregion import views

urlpatterns = [
    (r'^$', views.studyregion),
    url(r'^kml/$', views.regionKml, name='studyregion-kml'),
    (r'^kml/(\d+)/$', views.kml),
    (r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', views.regionKmlChunk),
    (r'^lookAtKml/$', views.regionLookAtKml),
    (r'^show/(\d+)/$', views.show),
]
