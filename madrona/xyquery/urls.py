from django.conf.urls import url, include
from madrona.xyquery import views

urlpatterns = [
        url(r'^$', views.query)
]
