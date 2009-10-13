from django.conf.urls.defaults import *

urlpatterns = patterns('simple.simple_app.views',
    (r'^simple-manipulators/$', 'simpleManipulators'),
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='sample-manipulator-list' ),
)