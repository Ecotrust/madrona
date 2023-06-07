from django.urls import re_path
from madrona.simplefaq.views import faq

urlpatterns = [
    re_path(r'^$', faq, name="simplefaq"),
]
