from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.help.views',
    url(r'^$', 'help', name="help-main"),
)
