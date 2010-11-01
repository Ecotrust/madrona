from django.conf.urls.defaults import *
from lingcod.rest import registered_models
from lingcod.common.utils import get_class
from lingcod.features import FeatureConfigurationError
import re

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

urlpatterns = []
for model in registered_models:
    name_underscore = convert(model.__name__)
    base_name = getattr(model.Rest, 'base_name', name_underscore)
    try:
        form_class = get_class(model.Rest.form)
    except:
        raise FeatureConfigurationError(
            """Feature class %s is not configured with a valid form class. 
            Could not import %s."""
             % (model.__name__, model.Rest.form))

    show_template = getattr(model.Rest, 'show_template', '%s/show.html' % (name_underscore, ))
    verbose_name = getattr(model.Rest, 'verbose_name', model.__name__)
    
    urlpatterns += patterns('lingcod.rest.views',
        url(r'%s/form/$' % (base_name,), 'form_resources', {'form_class': form_class, 'create_title': 'Create a New %s' % (verbose_name, )}, name='%s_create_form' % (name_underscore, )),
        url(r'%s/(?P<pk>\d+)/$' % (base_name, ), 'resource', {'form_class': form_class, 'template': show_template}, name='%s_resource' % (name_underscore, )),
        url(r'%s/(?P<pk>\d+)/form/$' % (base_name, ), 'form_resources', {'form_class': form_class}, name='%s_update_form' % (name_underscore, )),
    )