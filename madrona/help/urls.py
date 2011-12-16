from django.conf.urls.defaults import *

urlpatterns = patterns('madrona.help.views',
    url(r'^$', 'help', name="help-main"),
)
