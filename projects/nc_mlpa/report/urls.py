from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    (r'habitatrepresentation/mpa/(\d+)/(\w+)/$',mpa_habitat_representation),
    (r'habitatrepresentation/array/(\d+)/(\w+)/$',array_habitat_representation_summed),
    url(r'habitatreplication/array/(\d+)/(\w+)/$',array_habitat_replication, name='array_replication'),
)