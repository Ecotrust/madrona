from django.conf.urls.defaults import *
from django.contrib import admin
import django
import os

django_dir = os.path.dirname(django.__file__)
urlpatterns = patterns('',
    (r'^media/admin/(.*)', 
        'django.views.static.serve', 
        {
         'document_root' : os.path.join(django_dir, 'contrib', 'admin', 'static', 'admin'), 
         'show_indexes' : False
        }
    ),
)
admin.autodiscover()

urlpatterns += patterns('',
    (r'', include('madrona.common.urls')),
)
