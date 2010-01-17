from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.manipulators.views',
    (r'^test/$', 'testView' ),
    (r'^list/([A-Za-z0-9_,]+)/([A-Za-z0-9_,]+)/$', 'mpaManipulatorList' ),
    url(r'^([A-Za-z0-9_,]+)/$', 'multi_generic_manipulator_view', name='manipulate'),
)
