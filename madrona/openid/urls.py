# -*- coding: utf-8 -*-
# Copyright 2007, 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import url
from django.views.generic.base import TemplateView

# views
from django.contrib.auth import views as auth_views
from django.conf import settings
from madrona.openid import views as oid_views
from django_registration import views as reg_views
from django_registration.backends.activation import views as registration_views
activate = registration_views.ActivationView.activate
register = registration_views.RegistrationView.register
from madrona.common.registration_backend.forms import MadronaRegistrationForm

urlpatterns = [
    url(r'^password/reset/$', auth_views.PasswordResetView, name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.PasswordResetConfirmView,
        name='auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
        auth_views.PasswordResetCompleteView,
        name='auth_password_reset_complete'),
    url(r'^password/reset/done/$',
        auth_views.PasswordResetDoneView,
        name='auth_password_reset_done'),
    url(r'^password/$',oid_views.password_change, name='auth_password_change'),

    # manage account registration
    url(r'^associate/complete/$', oid_views.complete_associate, name='user_complete_associate'),
    url(r'^associate/$', oid_views.associate, name='user_associate'),
    url(r'^dissociate/$', oid_views.dissociate, name='user_dissociate'),
    url(r'^register/$', oid_views.register, name='user_register'),
    url(r'^signout/$', oid_views.signout, {'next_page':  settings.LOGIN_REDIRECT_URL}, name='user_signout'),
    url(r'^signout/$', oid_views.signout, {'next_page': settings.LOGIN_REDIRECT_URL}, name='auth_logout'),
    url(r'^signin/complete/$', oid_views.complete_signin, name='user_complete_signin'),
    url(
        r'^signup/$',
        register,
        {'backend': 'django_registration.backends.activation',
         'form_class': MadronaRegistrationForm},
        name='registration_register'
    ),
    url(r'^signup/complete/$',
        TemplateView.as_view(template_name='registration/registration_complete.html'),
        name='registration_complete'),

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
    url(r'^register/closed/$',
        TemplateView.as_view(template_name='registration/registration_closed.html'),
        name='registration_disallowed'),

    # yadis uri
    url(r'^yadis.xrdf$', oid_views.xrdf, name='oid_xrdf'),
]


## The openid login behavior can be 'hidden' by use of a
# template which only allows local user/pass authentication
# Note that this does not disable openid completely; user could still
# POST openid credentials if they wanted to
try:
    use_openid = settings.OPENID_ENABLED
except:
    use_openid = False

if use_openid:
    template_name = 'authopenid/signin.html'
else:
    template_name = 'authopenid/signin_local.html'

urlpatterns += [
    url(r'^signin/$', oid_views.signin, {'template_name':template_name}, name='user_signin'),
    url(r'^signin/$', oid_views.signin, {'template_name':template_name}, name='auth_login'),
]
