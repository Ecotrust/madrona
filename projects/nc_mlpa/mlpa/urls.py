from django.conf.urls.defaults import *


urlpatterns = patterns('mlpa.views',
    (r'^mpa/(\d+)/kmlAllGeom/$', 'mpaKmlAllGeom' ),
    (r'^mpa/(\d+)/kml/$', 'mpaKml' ),
    #the following line is used by studyregion/studyregion.html to obtain the request manipulator list from MlpaMpa
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='mpa-manipulator-list' ),
)
