from django.conf.urls.defaults import *


urlpatterns = patterns('mlpa.views',
    (r'^mpa/(\d+)/kmlAllGeom/$', 'mpaKmlAllGeom' ),
    (r'^mpa/(\d+)/kml/$', 'mpaKml' ),
    (r'^mlpa-manipulators/$', 'mlpaManipulators'),
)
