from django.conf.urls import url, include
from madrona.layer_manager import views

urlpatterns = [
    url(r'^layers.json$', views.get_json),
    url(r'^demo', views.demo)
]
