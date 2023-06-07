from django.urls import re_path, include
from madrona.layer_manager import views

urlpatterns = [
    re_path(r'^layers.json$', views.get_json),
    re_path(r'^demo', views.demo)
]
