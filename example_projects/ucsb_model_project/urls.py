from django.conf.urls.defaults import *
from lingcod.intersection.views import *


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^intersection/', include('lingcod.intersection.urls')),
    url(r'^admin/intersection/multifeatureshapefile/(\d+)/splitonfield/$', split_to_single_shapefiles, name='split_to_single_shapefiles'),
    # Example:
    # (r'^ucsb_model_project/', include('ucsb_model_project.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
