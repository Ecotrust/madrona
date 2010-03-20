from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'mpa/(\d+)/(\w+)', impact_analysis, name='mpa_impact_analysis'),
    url(r'mpa/(\d+)', impact_group_list, name='impact_group_list'),
    #(r'mpa/(\d+)', MpaEconAnalysis), #for testing purposes
    #url(r'mpa/print_report/(\d+)/([a-zA-Z\s]+)', print_report, name='printable_analysis'),
    #(r'test/', MpaEconAnalysisTest), #also for testing purposes
)  
