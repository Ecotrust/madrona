from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    #(r'multifeatureshapefile/splitbyfield/$',upload_intersection_feature),
    
    # (r'^login', 'django.contrib.auth.views.login'),
    (r'^intersect/testdrawing/$', test_drawing_intersect ),
    (r'^intersect/testpolygon/$', test_poly_intersect),    
    (r'^info/organization_scheme/(\d+)$', org_scheme_info ),
    (r'^info/organization_schemes/$', all_org_scheme_info ),
    (r'^(\w+)/(\w+)/(.*)$', organized_intersection_by_name ),
    (r'(\w+)/(.*)$', default_intersection ),
#    (r'^intersect/testpolygon/csv$', test_poly_intersect_csv),
)
