from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from django.views.generic.base import TemplateView, RedirectView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^madrona/', RedirectView.as_view(url='/')),    
    url(r'^$', 'madrona.common.views.map', {'template_name': 'common/map_ext.html'}, name="map"),    
    (r'^heatmap/', include('madrona.heatmap.urls')),
    (r'^tests/', TemplateView.as_view(template_name='common/tests.html'), 
        {'extra_context': {'api_key': settings.GOOGLE_API_KEY}}),
    
    # Include all madrona app urls. Any urls above will overwrite the common 
    # urls below
    (r'', include('madrona.common.urls')),
)
