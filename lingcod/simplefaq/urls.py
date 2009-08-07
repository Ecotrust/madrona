from django.conf.urls.defaults import *

urlpatterns = patterns('lingcod.simplefaq.views',
    (r'^$', 'faq' ),
)
