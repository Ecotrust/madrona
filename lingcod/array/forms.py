from django.forms import ModelForm
from django import forms
from lingcod.array.models import MpaArray
from lingcod.rest.forms import UserForm

class ArrayForm(UserForm):
    class Meta:
        model = MpaArray
        fields = ('user', 'name')
