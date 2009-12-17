from django.conf.urls.defaults import *

urlpatterns = patterns('',
	(r'^mpas/', include('lingcod.mpa.urls')),
	(r'^arrays/', include('lingcod.array.urls')),
	(r'^kml/', include('lingcod.kmlapp.urls')),
)