from django.urls import re_path
from madrona.screencasts import views

urlpatterns = [
    re_path(r'^$', views.listTutorials),
    re_path(r'^(\w+)/$', views.showVideo),
    re_path(r'^(?P<pk>\d)/show/$', views.showVideoByPk, name='screencasts-show-video'),
    re_path(r'^(?P<pk>\d+)/show_youtube/$', views.showYoutubeVideo, name='screencasts-show-youtube-video'),
]
