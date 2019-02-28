from django.conf.urls import url, include
from django.urls import reverse
from madrona.staticmap import views
urlpatterns = [
    url(r'^(?P<map_name>\w+)/$', views.show, name="staticmap-show"),
    url(r'^(?P<map_name>\w+)/$', views.staticmap_link, name="staticmap-link"),
    url(r'^$', views.show)
]
