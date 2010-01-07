from django.forms import ModelForm
from django import forms
from lingcod.mpa.models import *
from lingcod.mpa.models import Mpa
from lingcod.rest.forms import UserForm

class MpaForm(UserForm):
    geometry_orig = forms.CharField(widget=forms.HiddenInput())
    geometry_final = forms.CharField(widget=forms.HiddenInput())
    
    class Meta:
        model = Mpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')
    
    
class LoadForm(ModelForm):
    name = forms.CharField(max_length=100)
   
    class Meta:
        model = Mpa
        fields = ('user', 'name')
        