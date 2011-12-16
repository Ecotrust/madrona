from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    url(r'^potentialtargets/load_potential_targets', load_potential_targets_view, name='load_potential_targets'),
)