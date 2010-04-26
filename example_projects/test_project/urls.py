from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^$', 'lingcod.common.views.map', {'template_name': 'common/map.html'}, name="map"),
    (r'^tests/', 'django.views.generic.simple.direct_to_template', {'template': 'common/tests.html', 'extra_context': {'api_key': settings.GOOGLE_API_KEY}}),
    (r'^layers/', include('lingcod.layers.urls')),
    (r'^studyregion/', include('lingcod.studyregion.urls')),
    (r'^faq/', include('lingcod.simplefaq.urls')),
    (r'^help/', include('lingcod.help.urls')),
    (r'^kml/', include('lingcod.kmlapp.urls')),
    (r'^manipulators/', include('lingcod.manipulators.urls')),
    (r'^mpas/', include('lingcod.mpa.urls')),
    (r'^arrays/', include('lingcod.array.urls')),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': settings.LOGIN_REDIRECT_URL},  name='auth_logout'),
    (r'^accounts/profile/', include('lingcod.user_profile.urls')),
    (r'^accounts/', include('lingcod.common.registration_backend.urls')),
    (r'^intersection/', include('lingcod.intersection.urls')),
    (r'^screencasts/', include('lingcod.screencasts.urls')),
    (r'^sharing/', include('lingcod.sharing.urls')),
    (r'^staticmap/', include('lingcod.staticmap.urls')),
    (r'^news/', include('lingcod.news.urls')),
    (r'^admin/', include(admin.site.urls)),
)

# Useful for serving files when using the django dev server
urlpatterns += patterns('',
    (r'^media(.*)/upload/', 'lingcod.common.views.forbidden'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True }),
)

