from django.urls import re_path
from madrona.layers import views
import time


urlpatterns = [
    re_path(r'^public/$',
        views.get_public_layers,
        name='public-data-layers'),

    # Useful for debugging, avoids GE caching interference
    re_path(r'^public/cachebuster/%s' % str(time.time()),
        views.get_public_layers,
        name='public-data-layers-cachebuster'),

    re_path(r'^kml_file/(?P<session_key>\w+)/(?P<uid>[\w_]+).kml',
        views.get_kml_file,
        name='kml-file'),
    re_path(r'^privatekml/(?P<session_key>\w+)/$',
        views.get_privatekml_list,
        name='layers-privatekml-list'),
    re_path(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/$',
        views.get_privatekml,
        name='layers-privatekml'),
    re_path(r'^privatekml/(?P<session_key>\w+)/(?P<pk>\d+)/(?P<path>[^\n]+)$',
        views.get_relative_to_privatekml,
        name='layers-privatekml-relative'),
]
