from django.conf.urls import url, include
from madrona.loadshp import views

urlpatterns = [
    url(r'^single/$', views.load_single_shp, name='loadshp-single'),
]
