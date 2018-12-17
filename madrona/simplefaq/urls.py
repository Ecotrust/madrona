from django.conf.urls import patterns, url
from madrona.simplefaq.views import faq

urlpatterns = patterns('',
    url(r'^$', faq, name="simplefaq"),
)
