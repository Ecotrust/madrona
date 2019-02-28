from django.conf.urls import url, include
from django.urls import path
from madrona.screencasts import views

urlpatterns = [
    url(r'^$', views.listTutorials),
    url(r'^(\w+)/$', views.showVideo),
    url(r'^(?P<pk>\d)/show/$', views.showVideoByPk, name='screencasts-show-video'),
    url(r'^(?P<pk>\d+)/show_youtube/$', views.showYoutubeVideo, name='screencasts-show-youtube-video'),
]
