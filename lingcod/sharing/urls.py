from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.sharing.views',
    #url(r'^(?P<session_key>\w+)/(?P<object_type>\w+)/(?P<pk>\d+)/$', 'share_form', name='sharing-object-form'),
    url(r'^(?P<object_type>\w+)/(?P<pk>\d+)/$', 'share_form', name='sharing-object-form'),
)
