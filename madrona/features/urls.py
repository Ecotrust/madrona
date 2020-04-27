# from django.conf.urls import url, include
from django.urls import re_path, include
from madrona.common.utils import get_class
from madrona.features import registered_models, registered_links
from madrona.features import get_collection_models
from madrona.features import FeatureConfigurationError
from madrona.features import views
import re

urlpatterns = []
for model in registered_models:
    options = model.get_options()
    urlpatterns += [
        re_path(r'^%s/form/$' % (options.slug,), views.form_resources,
            kwargs={'model': model},
            name="%s_create_form" % (options.slug, )),

        re_path(r'^%s/(?P<uid>[\w_]+)/$' % (options.slug, ), views.resource,
            kwargs={'model': model},
            name='%s_resource' % (options.slug, )),

        re_path(r'^%s/(?P<uid>[\w_]+)/form/$' % (options.slug, ),
            views.form_resources, kwargs={'model': model},
            name='%s_update_form' % (options.slug,)),

        re_path(r'^%s/(?P<uid>[\w_]+)/share/$' % (options.slug, ),
            views.share_form, kwargs={'model': model},
            name='%s_share_form' % (options.slug,)),
    ]

for model in get_collection_models():
    options = model.get_options()
    urlpatterns += [
        re_path(r'^%s/(?P<collection_uid>[\w_]+)/remove/(?P<uids>[\w_,]+)$' % (options.slug, ),
            views.manage_collection, kwargs={'collection_model': model, 'action': 'remove'},
            name='%s_remove_features' % (options.slug,)),

        re_path(r'^%s/(?P<collection_uid>[\w_]+)/add/(?P<uids>[\w_,]+)$' % (options.slug, ),
            views.manage_collection, kwargs={'collection_model': model, 'action': 'add'},
            name='%s_add_features' % (options.slug,)),
    ]

for link in registered_links:
    url_path = r'^%s/links/%s/(?P<uids>[\w_,]+)/$' % (link.parent_slug, link.slug)
    urlpatterns += [
        re_path(url_path, views.handle_link, kwargs={'link': link},
            name=link.url_name)
    ]

urlpatterns += [
    re_path(r'^(?P<username>.+)/workspace-owner.json', views.workspace, kwargs={"is_owner": True}, name='workspace-owner-json'),
    re_path(r'^(?P<username>.+)/workspace-shared.json', views.workspace, kwargs={"is_owner": False}, name='workspace-shared-json'),
    re_path(r'^workspace-public.json', views.workspace, kwargs={"is_owner": False, "username": ''}, name='workspace-public-json'),
    re_path(r'^feature_tree.css', views.feature_tree_css, name='feature-tree-css'),
]
