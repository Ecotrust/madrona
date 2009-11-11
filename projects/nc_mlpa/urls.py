from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    
    url(r'^$', 'lingcod.common.views.map', name="map" ),
    
    (r'^tests/', 'django.views.generic.simple.direct_to_template', {'template': 'common/tests.html', 'extra_context': {'api_key': settings.GOOGLE_API_KEY}}),
    
    (r'^layers/', include('lingcod.layers.urls')),
    (r'^studyregion/', include('lingcod.studyregion.urls')),
    (r'^faq/', include('lingcod.simplefaq.urls')),
    (r'^wave/', include('lingcod.wave.urls')),
    (r'^manipulators/', include('lingcod.manipulators.urls')),
    (r'^manipulators-list/', 'nc_mlpa.views.manipulatorList'),
    #(r'^mpa/', include('lingcod.mpa.urls')),
    (r'^mpa/$', 'nc_mlpa.views.mlpaMpaCommit'),
    (r'^mpa/save/form/$', 'nc_mlpa.views.mlpaMpaCommit'),
    (r'^mpa/load/$', 'nc_mlpa.views.mlpaMpaLoad'),
    (r'^mpa/load/form/$', 'nc_mlpa.views.mlpaMpaLoadForm'),
    (r'^mlpa/', include('mlpa.urls')),
    
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)

# Useful for serving files when using the django dev server
urlpatterns += patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)
