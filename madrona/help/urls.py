from django.conf.urls import patterns, url, include

urlpatterns = patterns('madrona.help.views',
    url(r'^$', 'help', name="help-main"),
)
