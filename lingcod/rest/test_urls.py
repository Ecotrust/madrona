from django.conf.urls.defaults import *
from lingcod.rest.tests import RestTestModel, RestTestForm, get_view

urlpatterns = patterns('lingcod.rest.views',
    (r'^delete/(?P<pk>\d+)/$', 'delete', {'model': RestTestModel}),
    (r'^create/$', 'create', {'form_class': RestTestForm, 'action': '/create/'}),
    (r'^create/form/$', 'create_form', {'form_class': RestTestForm, 'action': '/create/'}),
    (r'^update/(?P<pk>\d+)/$', 'update', {'form_class': RestTestForm}),
    (r'^update/(?P<pk>\d+)/form/$', 'update_form', {'form_class': RestTestForm}),
    
    url(r'^rest_test_models/(?P<pk>\d+)/$', 'resource', {'form_class': RestTestForm}, name='rest_test_resource'),
)
