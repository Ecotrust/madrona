from django.urls import re_path, include
from django.contrib import admin
from django.conf import settings
from madrona.common import views
from django.views.static import serve

if settings.LAUNCH_PAGE:
    urlpatterns = [
        re_path(r'^$', views.launch, name='launch'),
        re_path(r'^map/', views.map, name='map'),
    ]
else:
    urlpatterns = [
        re_path(r'^$', views.map, name='map'),
    ]

urlpatterns += [
    re_path(r'^accounts/', include('madrona.openid.urls')),
    re_path(r'^accounts/', include('django_registration.backends.activation.urls')),
    re_path(r'^accounts/profile/', include('madrona.user_profile.urls')),
    re_path(r'^faq/', include('madrona.simplefaq.urls')),
    re_path(r'^features/', include('madrona.features.urls')),
    re_path(r'^help/', include('madrona.help.urls')),
    re_path(r'^kml/', include('madrona.kmlapp.urls')),
    re_path(r'^layers/', include('madrona.layers.urls')),
    re_path(r'^loadshp/', include('madrona.loadshp.urls')),
    re_path(r'^manipulators/', include('madrona.manipulators.urls')),
    re_path(r'^news/', include('madrona.news.urls')),
    re_path(r'^screencasts/', include('madrona.screencasts.urls')),
    re_path(r'^staticmap/', include('madrona.staticmap.urls')),
    re_path(r'^studyregion/', include('madrona.studyregion.urls')),
    re_path(r'^bookmark/', include('madrona.bookmarks.urls')),
    re_path(r'^layer_manager/', include('madrona.layer_manager.urls')),
    # Optional
    #re_path(r'^heatmap/', include('madrona.heatmap.urls')),
]

urlpatterns += [
    re_path(r'^admin/', admin.site.urls),
]

# Useful for serving files when using the django dev server
urlpatterns += [
    re_path(r'^media(.*)/upload/', views.forbidden),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
]
