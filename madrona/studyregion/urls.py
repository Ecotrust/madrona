from django.conf.urls import url, include
from madrona.studyregion import views

urlpatterns = [
    url(r'^$', views.studyregion),
    url(r'^kml/$', views.regionKml, name='studyregion-kml'),
    url(r'^kml/(\d+)/$', views.kml),
    url(r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', views.regionKmlChunk),
    url(r'^lookAtKml/$', views.regionLookAtKml),
    url(r'^show/(\d+)/$', views.show),
]
