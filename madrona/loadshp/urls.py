from django.urls import re_path
from madrona.loadshp import views

urlpatterns = [
    re_path(r'^single/$', views.load_single_shp, name='loadshp-single'),
]
