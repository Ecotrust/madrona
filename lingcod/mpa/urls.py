from django.conf.urls.defaults import *
from lingcod.common.utils import get_mpa_class
from lingcod.common.utils import get_mpa_form

urlpatterns = patterns('lingcod.mpa.views',
    # (r'^$', 'mpaCommit'),
    # (r'^save/form/$', 'mpaCommit'),
    # (r'^load/$', 'mpaLoad'),
    # (r'^load/form/$', 'mpaLoadForm'),
    url(r'^(?P<pk>\d+)/copy/$', 'copy', name="mpa-copy"),
    url(r'^clip/$', 'clip', name='mpa-clip'),
)