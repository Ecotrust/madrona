from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('madrona.common.views',
    # Main application window. Override by including another url pattern with 
    # an extended template by defining a url pattern in your project before 
    # including the common urls
    url(r'^$', 'map', name='map'),
)

urlpatterns += patterns('madrona',
    (r'^accounts/', include('madrona.openid.urls')),
    (r'^accounts/profile/', include('madrona.user_profile.urls')),
    (r'^faq/', include('madrona.simplefaq.urls')),
    (r'^features/', include('madrona.features.urls')),
    (r'^help/', include('madrona.help.urls')),
    (r'^kml/', include('madrona.kmlapp.urls')),
    (r'^layers/', include('madrona.layers.urls')),
    (r'^loadshp/', include('madrona.loadshp.urls')),
    (r'^manipulators/', include('madrona.manipulators.urls')),
    (r'^news/', include('madrona.news.urls')),
    (r'^screencasts/', include('madrona.screencasts.urls')),
    (r'^staticmap/', include('madrona.staticmap.urls')),
    (r'^studyregion/', include('madrona.studyregion.urls')),
    (r'^bookmark/', include('madrona.bookmarks.urls')),
    # Optional
    #(r'^spacing/', include('madrona.spacing.urls')),
    #(r'^heatmap/', include('madrona.heatmap.urls')),
    #(r'^data_manager/', include('madrona.data_manager.urls')),
    #(r'^admin/data_distributor', include('madrona.data_distributor.admin_urls')),
    #(r'^intersection/', include('madrona.intersection.urls')),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

# Useful for serving files when using the django dev server
urlpatterns += patterns('',
    (r'^media(.*)/upload/', 'madrona.common.views.forbidden'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)
