from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from lingcod import rest

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^marinemap/', 'django.views.generic.simple.redirect_to', {'url': '/'}),    
    url(r'^$', 'lingcod.common.views.map', {'template_name': 'common/map_ext.html'}, name="map"),    
    (r'^tests/', 'django.views.generic.simple.direct_to_template', {'template': 'common/tests.html', 'extra_context': {'api_key': settings.GOOGLE_API_KEY}}),
    (r'^kml/', include('lingcod.kmlapp.urls')),
    (r'^mpas/', include('lingcod.mpa.urls')),
    (r'^arrays/', include('lingcod.array.urls')),
    
    # Include all lingcod app urls. Any urls above will overwrite the common 
    # urls below
    (r'', include('lingcod.common.urls')),
)
