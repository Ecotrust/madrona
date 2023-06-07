from django.urls import reverse, re_path
from madrona.staticmap import views
urlpatterns = [
    re_path(r'^(?P<map_name>\w+)/$', views.show, name="staticmap-show"),
    re_path(r'^(?P<map_name>\w+)/$', views.staticmap_link, name="staticmap-link"),
    re_path(r'^$', views.show)
]
