from django.conf.urls.defaults import *
from lingcod.common.utils import get_class
from lingcod.features import registered_models, FeatureConfigurationError
import re

urlpatterns = []
for model in registered_models:
    config = model.get_config()
    urlpatterns += patterns('lingcod.features.views',
        url(r'%s/form/$' % (config.slug,), 'form_resources', kwargs={'model': model}, 
            name="%s_create_form" % (config.slug, )),
        url(r'%s/(?P<pk>\d+)/$' % (config.slug, ), 'resource', kwargs={'model': model}, 
            name='%s_resource' % (config.slug, )),
        url(r'%s/(?P<pk>\d+)/form/$' % (config.slug, ), 
            'form_resources', kwargs={'model': model}, name='%s_update_form' % (config.slug,)),
    )