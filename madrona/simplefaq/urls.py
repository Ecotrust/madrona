from django.conf.urls import url
from madrona.simplefaq.views import faq

urlpatterns = [
    url(r'^$', faq, name="simplefaq"),
]
