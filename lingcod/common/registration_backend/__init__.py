from registration.backends.default import DefaultBackend
from django.db import transaction
from django import forms
from django.contrib.sites.models import Site, RequestSite
from django.contrib.auth.models import User, Group
from registration.models import RegistrationManager, RegistrationProfile
from registration.forms import RegistrationForm
from registration import signals
from django.conf import settings

class CustomRegistrationForm(RegistrationForm):
    first_name = forms.CharField(label="First Name")
    last_name = forms.CharField(label="Last Name")

class LingcodBackend(DefaultBackend):
    def get_form_class(self, request):
        return CustomRegistrationForm

    def register(self, request, **kwargs):
        """
        Given a username, firstname, lastname, email address and password, 
        register a new user account, which will initially be inactive.

        See django-registration docs for more info
        """
        username, email, password, first, last = kwargs['username'], kwargs['email'], kwargs['password1'], \
                kwargs['first_name'], kwargs['last_name']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email, password, site)
        new_user.first_name = first
        new_user.last_name = last
        new_user.is_active = False
        webreg_group = Group.objects.get(name=settings.GROUP_REGISTERED_BY_WEB)
        new_user.groups.add(webreg_group)
        new_user.save()
        signals.user_registered.send(sender=self.__class__, user=new_user, request=request)
        return new_user


