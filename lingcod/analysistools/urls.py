from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.analysistools.views',
    url(r'^(?P<uid>[\w_]+)/progress.json$' , 'progress', name='analysis-progress'),
    url(r'^(?P<uid>[\w_]+)/progress.html$' , 'progress_html', name='analysis-html-progress'),
)


