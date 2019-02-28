from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin
from django.conf import settings
from madrona.common import views
from django.views.static import serve

if settings.LAUNCH_PAGE:
    urlpatterns = [
        url(r'^$', views.launch, name='launch'),
        url(r'^map/', views.map, name='map'),
    ]
else:
    urlpatterns = [
        url(r'^$', views.map, name='map'),
    ]

urlpatterns += [
    path(r'^accounts/', include('madrona.openid.urls')),
    path(r'^accounts/', include('django_registration.backends.activation.urls')),
    path(r'^accounts/profile/', include('madrona.user_profile.urls')),
    path(r'^faq/', include('madrona.simplefaq.urls')),
    path(r'^features/', include('madrona.features.urls')),
    path(r'^help/', include('madrona.help.urls')),
    path(r'^kml/', include('madrona.kmlapp.urls')),
    path(r'^layers/', include('madrona.layers.urls')),
    path(r'^loadshp/', include('madrona.loadshp.urls')),
    path(r'^manipulators/', include('madrona.manipulators.urls')),
    path(r'^news/', include('madrona.news.urls')),
    path(r'^screencasts/', include('madrona.screencasts.urls')),
    path(r'^staticmap/', include('madrona.staticmap.urls')),
    path(r'^studyregion/', include('madrona.studyregion.urls')),
    path(r'^bookmark/', include('madrona.bookmarks.urls')),
    path(r'^layer_manager/', include('madrona.layer_manager.urls')),
    # Optional
    #path(r'^heatmap/', include('madrona.heatmap.urls')),
]

urlpatterns += [
    url(r'^admin/', admin.site.urls),
]

# Useful for serving files when using the django dev server
urlpatterns += [
    url(r'^media(.*)/upload/', views.forbidden),
    url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
]
