from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('lingcod.common.views',
    # Main application window. Override by including another url pattern with 
    # an extended template by defining a url pattern in your project before 
    # including the common urls
    url(r'^$', 'map', name='map'),
)

urlpatterns += patterns('lingcod',
    (r'^layers/', include('lingcod.layers.urls')),
    (r'^studyregion/', include('lingcod.studyregion.urls')),
    (r'^faq/', include('lingcod.simplefaq.urls')),
    (r'^help/', include('lingcod.help.urls')),
    (r'^manipulators/', include('lingcod.manipulators.urls')),
    (r'^accounts/', include('lingcod.openid.urls')),
    (r'^accounts/profile/', include('lingcod.user_profile.urls')),
    (r'^intersection/', include('lingcod.intersection.urls')),
    (r'^screencasts/', include('lingcod.screencasts.urls')),
    (r'^sharing/', include('lingcod.sharing.urls')),
    (r'^staticmap/', include('lingcod.staticmap.urls')),
    (r'^news/', include('lingcod.news.urls')),
    (r'^spacing/', include('lingcod.spacing.urls')),
    (r'^heatmap/', include('lingcod.heatmap.urls')),
    (r'^data_manager/', include('lingcod.data_manager.urls')),
    (r'^admin/data_distributor', include('lingcod.data_distributor.admin_urls')),
    (r'^features/', include('lingcod.features.urls')),
)

urlpatterns += patterns('',
    (r'^admin/', include(admin.site.urls)),
)

# Useful for serving files when using the django dev server
urlpatterns += patterns('',
    (r'^media(.*)/upload/', 'lingcod.common.views.forbidden'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)