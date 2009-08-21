from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.studyregion.views',
    (r'^$', 'studyregion' ),
    (r'^kml/(\d+)/$', 'kml'),
    (r'^kml/$', 'regionKml' ),
    (r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', 'regionKmlChunk' ),
    (r'^lookAtKml/$', 'regionLookAtKml' ),
    (r'^show/(\d+)/$', 'show' ),
)
