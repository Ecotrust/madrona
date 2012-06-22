from django.conf.urls.defaults import *
from madrona.common.utils import get_class
from views import *
import os

urlpatterns = []

urlpatterns += patterns('madrona.layer_manager.views',
    (r'^get_json', getJson)
)
