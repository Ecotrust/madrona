from django.conf.urls.defaults import *
from views import *
  
urlpatterns = patterns('',
    url(r'spacing/array/(\d+)/$', array_cluster_spacing_excel, name='array_cluster_spacing_excel'),
    url(r'shapefile/array/(?P<array_id_list_str>(\d+,?)+)/$', array_shapefile,name='array_shapefile'),
    url(r'shapefile/mpa/(?P<mpa_id_list_str>(\d+,?)+)/$', mpa_shapefile,name='mpa_shapefile'),
    url(r'habitatrepresentation/mpa/(\d+)/(\w+)/$',mpa_habitat_representation, name='mpa_habitat_representation'),
    (r'habitatrepresentation/array/(\d+)/(\w+)/$',array_habitat_representation_summed),
    url(r'habitatreplication/array/(\d+)/(\w+)/$',array_habitat_replication, name='array_replication'),
    url(r'habitatspacing/array/(\d+)/(\w+)/$',array_spacing_report, name='array_spacing'),
    url(r'spacingkml/array/(\d+)/(\d+)/(\w+)/$',array_spacing_kml, name='array_spacing_kml'),
    url(r'habitatspreadsheet/array/(?P<array_id_list_str>(\d+,?)+)/$',array_list_habitat_excel, name='array_habitat_spreadsheet'),
    url(r'summary/array/(?P<array_id_list_str>(\d+,?)+)/$',array_summary_excel,name='array_summary_excel'),
)