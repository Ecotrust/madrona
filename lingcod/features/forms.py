# Need a UserForm base class here
# from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class ShapeInput(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        kml = ''
        if name == 'geometry_final':
            output = super(ShapeInput, self).render(name, '', attrs)
        else:
            output = super(ShapeInput, self).render(name, value, attrs)
        if value:
            geo = fromstr(value)
            geo.srid = GEOMETRY_DB_SRID
            kml = display_kml(geo)
        return mark_safe("""
        <script id="%s_kml" type="application/vnd.google-earth.kml+xml">
        %s
        </script>
        %s
        """ % (name, kml, output))
            
class FeatureForm(ModelForm):
    user = forms.ModelChoiceField(User.objects.all(),widget=forms.HiddenInput())
    geometry_orig = forms.CharField(widget=ShapeInput())
    geometry_final = forms.CharField(widget=ShapeInput(), required=False)
    manipulators = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        exclude = ('sharing_groups','content_type','object_id',)
