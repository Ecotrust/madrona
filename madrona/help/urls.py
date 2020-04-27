from django.conf.urls import url, include
from madrona.help import views

urlpatterns = [
    url(r'^$', views.help, name="help-main"),
]
