from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.wave.views',
    url(r'^snapshot/', 'snapshot_gadget', name='snapshot_gadget'),
)
