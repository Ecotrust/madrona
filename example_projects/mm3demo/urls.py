from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Include all lingcod app urls. Any urls above will overwrite the common 
    # urls below
    (r'', include('lingcod.common.urls')),
)
