from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from madrona.common import views

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
    (r'^accounts/', include('madrona.openid.urls')),
    (r'^accounts/', include('django_registration.backends.activation.urls')),
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
    (r'^layer_manager/', include('madrona.layer_manager.urls')),
    # Optional
    #(r'^heatmap/', include('madrona.heatmap.urls')),
]

urlpatterns += [
    (r'^admin/', include(admin.site.urls)),
]

# Useful for serving files when using the django dev server
urlpatterns += [
    (r'^media(.*)/upload/', views.forbidden),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
]
