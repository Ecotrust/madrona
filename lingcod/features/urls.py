from django.conf.urls.defaults import *
from lingcod.common.utils import get_class
from lingcod.features import registered_models, registered_links
from lingcod.features import get_collection_models
from lingcod.features import FeatureConfigurationError
import re

urlpatterns = []
for model in registered_models:
    options = model.get_options()
    urlpatterns += patterns('lingcod.features.views',
        url(r'^%s/form/$' % (options.slug,), 'form_resources', 
            kwargs={'model': model}, 
            name="%s_create_form" % (options.slug, )),
            
        url(r'^%s/(?P<uid>[\w_]+)/$' % (options.slug, ), 'resource', 
            kwargs={'model': model}, 
            name='%s_resource' % (options.slug, )),
            
        url(r'^%s/(?P<uid>[\w_]+)/form/$' % (options.slug, ), 
            'form_resources', kwargs={'model': model}, 
            name='%s_update_form' % (options.slug,)),

        url(r'^%s/(?P<uid>[\w_]+)/share/$' % (options.slug, ), 
            'share_form', kwargs={'model': model}, 
            name='%s_share_form' % (options.slug,)),
    )

for model in get_collection_models():
    options = model.get_options()
    urlpatterns += patterns('lingcod.features.views',
        url(r'^%s/(?P<collection_uid>\d+)/remove/(?P<uids>[\w_,]+)$' % (options.slug, ), 
            'manage_collection', kwargs={'collection_model': model, 'action': 'remove'}, 
            name='%s_remove_features' % (options.slug,)),

        url(r'^%s/(?P<collection_uid>\d+)/add/(?P<uids>[\w_,]+)$' % (options.slug, ), 
            'manage_collection', kwargs={'collection_model': model, 'action': 'add'}, 
            name='%s_add_features' % (options.slug,)),
    )

for link in registered_links:
    path = r'^%s/links/%s/(?P<uids>[\w_,]+)/$' % (link.parent_slug, link.slug)
    urlpatterns += patterns('lingcod.features.views',
        url(path, 'handle_link', kwargs={'link': link}, 
            name=link.url_name)
    )

urlpatterns += patterns('lingcod.features.views',
    url(r'^workspace.json', 'workspace', name='workspace-json'),)

