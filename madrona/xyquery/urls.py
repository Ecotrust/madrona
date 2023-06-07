from django.urls import re_path
from madrona.xyquery import views

urlpatterns = [
        re_path(r'^$', views.query)
]
