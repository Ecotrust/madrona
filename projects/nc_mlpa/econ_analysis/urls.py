from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    (r'mpa/(\d+)', MpaEconAnalysis),
)  
