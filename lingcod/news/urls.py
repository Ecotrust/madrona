from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('lingcod.news.views',
    url(r'^$', 'main', name='news-main'),
    url(r'^about/$', direct_to_template, {'template':'about.html'}, name='news-about'),
)
