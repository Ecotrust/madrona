from django.conf.urls.defaults import *
from lingcod.common.utils import get_array_form

urlpatterns = patterns('lingcod.array.views',
)

ArrayForm = get_array_form()

urlpatterns += patterns('lingcod.rest.views',
    url(r'^form/$', 'form_resources', {'form_class': ArrayForm, 'create_title': 'Create a New Array'}, name='array_create_form'),
    url(r'^(?P<pk>\d+)/$', 'resource', {'form_class': ArrayForm}, name='array_resource'),
    url(r'^(?P<pk>\d+)/form/$', 'form_resources', {'form_class': ArrayForm}, name='array_update_form'),
)