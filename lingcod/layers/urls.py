from django.conf.urls.defaults import *


urlpatterns = patterns('lingcod.layers.views',
    url(r'^public/', 'get_public_layers', name='public-data-layers'),
    url(r'^ecotrust/$', 'get_ecotrust_layers', name='ecotrust-data-layers'),
    url(r'^ecotrust/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_map'),
    url(r'^ecotrust/tiles/contour/([A-Za-z]+)/([A-Za-z0-9_,]+)/$', 'get_contour'),
    #note on the following 2 url patterns:
    #providing for an optional trailing slash ('/') to prevent GE big red X's generated from missed url attempts (301's)
    url(r'^ecotrust/tiles/map/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_map'),
    url(r'^ecotrust/tiles/contour/([A-Za-z]+)/([A-Za-z0-9_,]+)/([0-9]+)/([0-9]+)/([0-9]+)\.([A-Za-z]+)/?$', 'get_contour'),    
)
