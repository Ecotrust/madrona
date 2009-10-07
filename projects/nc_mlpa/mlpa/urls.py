from django.conf.urls.defaults import *


urlpatterns = patterns('mlpa.views',
    (r'^mpa/(\d+)/kmlAllGeom/$', 'mpaKmlAllGeom' ),
    (r'^mpa/(\d+)/kml/$', 'mpaKml' ),
    (r'^mlpa-manipulators/$', 'mlpaManipulators'),
    #the following pattern is used by mlpa-maniuplators.html to obtain the requested manipulator list from MlpaMpa
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='mpa-manipulator-list' ),
)
