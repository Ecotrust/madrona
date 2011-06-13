# Need a UserForm base class here
from django.db import models
from django import forms
from django.forms import ModelForm
from lingcod.features.forms import FeatureForm as UserForm

class ShapeForm(UserForm):
    def as_p(self, *args, **kwargs):
        # return False
        output = super(ShapeForm, self).as_p(*args, **kwargs)
        return output
