from django.conf.urls.defaults import *


urlpatterns = patterns('mlpa.views',
    (r'^mlpa-manipulators/$', 'mlpaManipulators'),
)
