from django.urls import re_path
from madrona.help import views

urlpatterns = [
    re_path(r'^$', views.help, name="help-main"),
]
