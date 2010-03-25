from django.conf.urls.defaults import *


urlpatterns = patterns('nc_mlpa.ecotrust_layers.views',
    #url(r'^ecotrust/$', 'get_ecotrust_layers', name='ecotrust-data-layers'),
    url(r'^(?P<session_key>\w+)/(?P<input_username>\w+)/ecotrust/$', 'get_ecotrust_layers', name='ecotrust-data-layers'),
    url(r'^(\w+)/(\w+)/ecotrust/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^(\w+)/(\w+)/ecotrust/tiles/contour/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_contour'),
    url(r'^(\w+)/(\w+)/ecotrust/other/([A-Za-z]+)/([A-Za-z0-9_,-\.]+)/$', 'get_other'),
    #note on the following 2 url patterns:
    #providing for an optional trailing slash ('/') to prevent GE big red X's generated from missed url attempts (301's)
    url(r'^(\w+)/(\w+)/ecotrust/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
    url(r'^(\w+)/(\w+)/ecotrust/tiles/contour/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_contour'),    
)
