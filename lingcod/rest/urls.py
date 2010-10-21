from django.conf.urls.defaults import *
from lingcod.rest import registered_models

urlpatterns = []
for model in registered_models:
    
    urlpatterns += patterns('',
        (r'%s/' % (str(model.__name__),), 'lingcod.common.views.forbidden'),
        # url(r'^form/$', 'form_resources', {'form_class': MpaForm, 'create_title': 'Create a New Marine Protected Area'}, name='mpa_create_form'),
        # url(r'^(?P<pk>\d+)/$', 'resource', {'form_class': MpaForm, 'template': 'mpa/show.html'}, name='mpa_resource'),
        # url(r'^(?P<pk>\d+)/form/$', 'form_resources', {'form_class': MpaForm}, name='mpa_update_form'),
    )
    print "registering url for " + str(model)