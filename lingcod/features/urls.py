from django.conf.urls.defaults import *
from lingcod.common.utils import get_class
from lingcod.features import registered_models, registered_links
from lingcod.features import FeatureConfigurationError
import re

urlpatterns = []
for model in registered_models:
    options = model.get_options()
    urlpatterns += patterns('lingcod.features.views',
        url(r'%s/form/$' % (options.slug,), 'form_resources', 
            kwargs={'model': model}, 
            name="%s_create_form" % (options.slug, )),
            
        url(r'%s/(?P<pk>\d+)/$' % (options.slug, ), 'resource', 
            kwargs={'model': model}, 
            name='%s_resource' % (options.slug, )),
            
        url(r'%s/(?P<pk>\d+)/form/$' % (options.slug, ), 
            'form_resources', kwargs={'model': model}, 
            name='%s_update_form' % (options.slug,)),

        url(r'%s/(?P<pk>\d+)/share/$' % (options.slug, ), 
            'share_form', kwargs={'model': model}, 
            name='%s_share_form' % (options.slug,)),
    )

for link in registered_links:
    path = r'%s/links/%s/(?P<ids>[\w_,]+)/$' % (link.parent_slug, link.slug)
    urlpatterns += patterns('lingcod.features.views',
        url(path, 'handle_link', kwargs={'link': link}, 
            name=link.url_name)
    )
