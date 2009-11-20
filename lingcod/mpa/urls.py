from django.conf.urls.defaults import *
from lingcod.common.utils import get_mpa_class

urlpatterns = patterns('lingcod.mpa.views',
    (r'^$', 'mpaCommit'),
    (r'^save/form/$', 'mpaCommit'),
    (r'^load/$', 'mpaLoad'),
    (r'^load/form/$', 'mpaLoadForm'),
    (r'^(?P<pk>\d)/$', 'lingcod.rest.views.resource', {'model': get_mpa_class, 'get_func': lingcod.mpa.views.get_mpa}),
)
