from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.studyregion.views',
    (r'^$', 'studyregion' ),
    (r'^kml/$', 'regionKml' ),
    (r'^kml_chunk/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/([-]?\d+\.\d+)/$', 'regionKmlChunk' ),
    (r'^lookAtKml/$', 'regionLookAtKml' ),
)
