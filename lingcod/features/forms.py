# Need a UserForm base class here
# from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

class FeatureForm(ModelForm):
    user = forms.ModelChoiceField(User.objects.all(), 
        widget=forms.HiddenInput())