from django.conf.urls import patterns, url, include


urlpatterns = patterns('madrona.screencasts.views',
    (r'^$', 'listTutorials'),
    (r'^(\w+)/$', 'showVideo'),
    url(r'^(?P<pk>\d)/show/$', 'showVideoByPk', name='screencasts-show-video'),
    url(r'^(?P<pk>\d+)/show_youtube/$', 'showYoutubeVideo', name='screencasts-show-youtube-video'),
)
