# Need a UserForm base class here
from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import *

class UserForm(ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), widget=forms.HiddenInput())