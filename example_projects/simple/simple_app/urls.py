from django.conf.urls.defaults import *

urlpatterns = patterns('simple.simple_app.views',
    (r'^simple-manipulators/$', 'simpleManipulators'),
)