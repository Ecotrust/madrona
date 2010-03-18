from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'mpa/(\d+)/(\w+)/(\w+)', impact_analysis, name='mpa_impact_analysis'),
    url(r'mpa/(\d+)/(\w+)', impact_group_list, name='impact_group_list'),
    #(r'mpa/(\d+)', MpaEconAnalysis), #for testing purposes
    url(r'mpa/(\d+)', printable_analysis, name='printable_analysis'),
    #(r'test/', MpaEconAnalysisTest), #also for testing purposes
)  
