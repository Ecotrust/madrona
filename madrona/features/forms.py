# Need a UserForm base class here
# from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.gis.geos import fromstr
from django.conf import settings
from madrona.manipulators.manipulators import display_kml

class ShapeInput(forms.HiddenInput):
    def render(self, name, value, attrs=None, renderer=None):
        from madrona.features.models import PolygonFeature, PointFeature, LineFeature
        model = self.form_instance.Meta.model
        if issubclass(model, PolygonFeature):
            type = 'polygon'
        elif issubclass(model, LineFeature):
            type = 'linestring'
        else:
            type = 'point'
        kml = ''
        if name == 'geometry_final':
            output = super(ShapeInput, self).render(name, '', attrs)
        else:
            output = super(ShapeInput, self).render(name, value, attrs)
        if value:
            geo = fromstr(value)
            geo.srid = settings.GEOMETRY_DB_SRID
            kml = display_kml(geo)
        return mark_safe("""
        <script class="%s" id="%s_kml" type="application/vnd.google-earth.kml+xml">
        %s
        </script>
        %s
        """ % (type, name, kml, output))

class FeatureForm(ModelForm):
    user = forms.ModelChoiceField(User.objects.all(),widget=forms.HiddenInput())

    class Meta:
        exclude = ('sharing_groups','content_type','object_id',)

class SpatialFeatureForm(FeatureForm):
    geometry_orig = forms.CharField(widget=ShapeInput())
    geometry_final = forms.CharField(widget=ShapeInput(), required=False)
    manipulators = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        exclude = ('sharing_groups','content_type','object_id',)

    def __init__(self, *args, **kwargs):
        super(SpatialFeatureForm, self).__init__(*args, **kwargs)
        self.fields['geometry_final'].widget.form_instance = self
        self.fields['geometry_orig'].widget.form_instance = self
