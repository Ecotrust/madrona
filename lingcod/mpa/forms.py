from django.forms import ModelForm
from django import forms
from lingcod.mpa.models import *


class MpaForm(ModelForm):
    name = forms.CharField(max_length=100)
    
    class Meta:
        model = Mpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')
    
    
class LoadForm(ModelForm):
    name = forms.CharField(max_length=100)
   
    class Meta:
        model = Mpa
        fields = ('user', 'name')
        