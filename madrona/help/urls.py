from django.conf.urls import *

urlpatterns = patterns('madrona.help.views',
    url(r'^$', 'help', name="help-main"),
)
