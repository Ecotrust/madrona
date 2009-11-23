from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.screencasts.views',   
    (r'^$', 'listTutorials'),  
    (r'^(\w+)/$', 'showVideo'),
)
