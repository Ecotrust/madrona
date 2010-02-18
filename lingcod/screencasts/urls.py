from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.screencasts.views',   
    (r'^$', 'listTutorials'),  
    (r'^(\w+)/$', 'showVideo'),
    url(r'^(?P<pk>\d)/show/$', 'showVideoByPk', name='screencasts-show-video'),
)
