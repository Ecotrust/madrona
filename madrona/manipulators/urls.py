from django.conf.urls import patterns, url, include

urlpatterns = patterns('madrona.manipulators.views',
    (r'^test/$', 'testView'),
    (r'^list/([A-Za-z0-9_,]+)/([A-Za-z0-9_,]+)/$', 'mpaManipulatorList'),
    url(r'^([A-Za-z0-9_,]+)/$', 'multi_generic_manipulator_view', name='manipulate'),
    url(r'^$', 'multi_generic_manipulator_view', {'manipulators': None}, name='manipulate-blank'),
    url(r'^/$', 'multi_generic_manipulator_view', {'manipulators': None}, name='manipulate-blank'),
)
