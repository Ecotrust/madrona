from django.conf.urls.defaults import *

urlpatterns = patterns('madrona.simplefaq.views',
    (r'^$', 'faq' ),
)
