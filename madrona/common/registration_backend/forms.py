#!/usr/bin/python
from django_registration.forms import RegistrationForm
from django import forms

attrs_dict = {
        'class': 'required',
#        'onchange':'alert("check your self, fool");'
}

class MadronaRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=r'^\w+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label="Username",
        error_messages={'invalid': "Username can contain only letters, numbers or underscores (spaces are not permitted)."})
