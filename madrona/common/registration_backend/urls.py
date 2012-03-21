"""
URLconf for registration and activation, using django-registration's
default backend.
"""
from django.conf.urls.defaults import *
from django.views.generic.base import TemplateView
from registration.views import activate
from registration.views import register
from django.conf import settings

urlpatterns = patterns('',
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='registration/activation_complete.html'),
        {'extra_context': {'group_request_email': settings.GROUP_REQUEST_EMAIL}},
        name='registration_activation_complete'),
    # Activation keys get matched by \w+ instead of the more specific
    # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
    # that way it can return a sensible "invalid key" message instead of a
    # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        {'backend': 'madrona.common.registration_backend.LingcodBackend'},
        name='registration_activate'),
    url(r'^register/$',
        register,
        {'backend': 'madrona.common.registration_backend.LingcodBackend'},
        name='registration_register'),
    url(r'^register/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),
        name='registration_complete'),
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),
    (r'', include('registration.auth_urls')),
)
