from django.conf.urls.defaults import patterns, url
from madrona.simplefaq.views import faq

urlpatterns = patterns('',
    url(r'^$', faq, name="simplefaq"),
)
