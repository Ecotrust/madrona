from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    (r'habitatrepresentation/mpa/(\d+)/(\w+)$',mpa_habitat_representation),
)