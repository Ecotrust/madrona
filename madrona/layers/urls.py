from django.conf.urls import url, include
from madrona.layers import views
import time


urlpatterns = [
    url(r'^public/$',
        views.get_public_layers,
        name='public-data-layers'),

    # Useful for debugging, avoids GE caching interference
    url(r'^public/cachebuster/%s' % str(time.time()),
        views.get_public_layers,
        name='public-data-layers-cachebuster'),

    url(r'^kml_file/(?P<session_key>\w+)/(?P<uid>[\w_]+).kml',
        views.get_kml_file,
        name='kml-file'),
    url(r'^privatekml/(?P<session_key>\w+)/$',
        views.get_privatekml_list,
        name='layers-privatekml-list'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/$',
        views.get_privatekml,
        name='layers-privatekml'),
    url(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/(?P<path>[^\n]+)$',
        views.get_relative_to_privatekml,
        name='layers-privatekml-relative'),
]
