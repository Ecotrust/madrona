from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    url(r'^nothing', nothing, name='nothing'),
)