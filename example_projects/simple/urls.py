from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'lingcod.common.views.map', {'template_name': 'common/map-ext.html'}),
    (r'^tests/', 'django.views.generic.simple.direct_to_template', {'template': 'common/tests.html', 'extra_context': {'api_key': settings.GOOGLE_API_KEY}}),
    (r'^layers/', include('lingcod.layers.urls')),
    (r'^studyregion/', include('lingcod.studyregion.urls')),
    (r'^faq/', include('lingcod.simplefaq.urls')),
    (r'^staticmap/', include('lingcod.staticmap.urls')),
    (r'^kml/', include('lingcod.kmlapp.urls')),
    (r'^wave/', include('lingcod.wave.urls')),
    (r'^manipulators/', include('lingcod.manipulators.urls')),
    #(r'^manipulators-list/', 'simple.views.manipulatorList'), 
    #(r'^mpa/', include('lingcod.mpa.urls')),
    # (r'^mpa/$', 'simple.views.simpleCommit'),
    # (r'^mpa/save/form/$', 'simple.views.simpleCommit'),
    # (r'^mpa/load/$', 'simple.views.simpleLoad'),
    # (r'^mpa/load/form/$', 'simple.views.simpleLoadForm'),
    (r'^simple-app/', include('simple.simple_app.urls')),
    
    (r'^mpas/', include('lingcod.mpa.urls')),
    (r'^arrays/', include('lingcod.array.urls')),
    # (r'^data_distributor/', include('lingcod.data_distributor.urls')),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name='logout'),
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
