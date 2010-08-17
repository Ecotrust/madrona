from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    url(r'^array/geotiff/(?P<array_id_list_str>(\d+,?)+)/$',overlap_geotiff_response, name='heatmap-array-geotiff'),
    url(r'^array/kml/(?P<array_id_list_str>(\d+,?)+)/$',overlap_kml_response, name='heatmap-array-kml'),
)
