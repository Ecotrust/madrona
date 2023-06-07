from django.urls import re_path
from madrona.studyregion import views

urlpatterns = [
    re_path(r'^$', views.studyregion),
    re_path(r'^kml/$', views.regionKml, name='studyregion-kml'),
    re_path(r'^kml/(\d+)/$', views.kml),
    re_path(r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', views.regionKmlChunk),
    re_path(r'^lookAtKml/$', views.regionLookAtKml),
    re_path(r'^show/(\d+)/$', views.show),
]
