from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    url(r'^generalfile/download/(\d+)/$',return_active_general_file,name='return_active_general_file'),
)