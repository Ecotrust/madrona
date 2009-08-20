from django.conf.urls.defaults import *


urlpatterns = patterns('mlpa.views',
    (r'^mpa/(\d+)/kmlAllGeom/$', 'mpaKmlAllGeom' ),
    (r'^mpa/(\d+)/kml/$', 'mpaKml' ),
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='mpa-manipulator-list' ),
)
