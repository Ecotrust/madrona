from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.mpa.views',
    (r'^$', 'mpaCommit'),
    (r'^save/form/$', 'mpaCommit'),
    (r'^load/$', 'mpaLoad'),
    (r'^load/form/$', 'mpaLoadForm'),
)
