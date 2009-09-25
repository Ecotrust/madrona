from django.conf.urls.defaults import *

urlpatterns = patterns('simple.simple_app.views',
    (r'^sample/manipulator/$', 'sampleManipulator'),
    url(r'^mpa/manipulators/$', 'mpaManipulatorList', name='sample-manipulator-list' ),
)