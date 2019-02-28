from django.conf.urls import url, include
from madrona.screencasts import views

urlpatterns = [
    (r'^$', views.listTutorials),
    (r'^(\w+)/$', views.showVideo),
    url(r'^(?P<pk>\d)/show/$', views.showVideoByPk, name='screencasts-show-video'),
    url(r'^(?P<pk>\d+)/show_youtube/$', views.showYoutubeVideo, name='screencasts-show-youtube-video'),
]
