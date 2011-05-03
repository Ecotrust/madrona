from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.analysistools.views',
    url(r'^(?P<uid>[\w_]+)/progress.json$' , 'progress', name='analysis-progress'),
)


