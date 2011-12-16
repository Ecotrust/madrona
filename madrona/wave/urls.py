from django.conf.urls.defaults import *


urlpatterns = patterns('madrona.wave.views',
    url(r'^snapshot/', 'snapshot_gadget', name='snapshot_gadget'),
)
