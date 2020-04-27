from django.conf.urls import patterns, url, include

urlpatterns = patterns('madrona.analysistools.views',
    url(r'^(?P<uid>[\w_]+)/progress.json$', 'progress', name='analysis-progress'),
    url(r'^(?P<uid>[\w_]+)/progress.html$', 'progress_html', name='analysis-html-progress'),
)
