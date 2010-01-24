from django.conf.urls.defaults import *
from lingcod.common.utils import get_mpa_class
from lingcod.common.utils import get_mpa_form

urlpatterns = patterns('lingcod.mpa.views',
    # (r'^$', 'mpaCommit'),
    # (r'^save/form/$', 'mpaCommit'),
    # (r'^load/$', 'mpaLoad'),
    # (r'^load/form/$', 'mpaLoadForm'),
    # (r'^(?P<pk>\d)/$', 'lingcod.rest.views.resource', {'model': get_mpa_class, 'get_func': lingcod.mpa.views.get_mpa}),
)

MpaForm = get_mpa_form()

urlpatterns += patterns('lingcod.rest.views',
    url(r'^form/$', 'form_resources', {'form_class': MpaForm, 'create_title': 'Create a New Marine Protected Area'}, name='mpa_create_form'),
    url(r'^(?P<pk>\d+)/$', 'resource', {'form_class': MpaForm, 'template': 'mpa/show.html'}, name='mpa_resource'),
    url(r'^(?P<pk>\d+)/form/$', 'form_resources', {'form_class': MpaForm}, name='mpa_update_form'),
)