from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.studyregion.views',
    (r'^kml/$', 'regionKml' ),
    (r'^lookAtKml/$', 'regionLookAtKml' ),
)
