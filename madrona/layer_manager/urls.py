from django.conf.urls.defaults import *
from views import get_json

urlpatterns = patterns('madrona.layer_manager.views',
    (r'^get_json', get_json)
)
