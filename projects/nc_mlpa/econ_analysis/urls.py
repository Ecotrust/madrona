from django.conf.urls.defaults import *
from views import *

urlpatterns = patterns('',
    url(r'mpa/(\d+)/(\w+)', impact_analysis, name='mpa_impact_analysis'),
    (r'mpa/(\d+)', MpaEconAnalysis),
    url(r'mpa/printable/(\d+)', printable_analysis, name='printable_analysis'),
    (r'test/', MpaEconAnalysisTest),
)  
