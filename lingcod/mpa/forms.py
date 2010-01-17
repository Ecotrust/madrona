from django.forms import ModelForm
from django import forms
from lingcod.mpa.models import *
from lingcod.mpa.models import Mpa
from lingcod.rest.forms import UserForm
from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.geos import fromstr
from django.conf import settings
from settings import GEOMETRY_CLIENT_SRID, GEOMETRY_DB_SRID
    
class LoadForm(ModelForm):
    name = forms.CharField(max_length=100)
   
    class Meta:
        model = Mpa
        fields = ('user', 'name')


class ShapeInput(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        if value:
            geo = fromstr(value)
            if geo.srid != GEOMETRY_CLIENT_SRID:
                geo.srid = GEOMETRY_DB_SRID
                geo.transform(GEOMETRY_CLIENT_SRID)
            value = geo.ewkt
        return super(ShapeInput, self).render(name, value, attrs)
        
class MpaForm(UserForm):
    geometry_orig = forms.CharField(widget=ShapeInput())
    geometry_final = forms.CharField(widget=ShapeInput())

    class Meta:
        model = Mpa
        fields = ('user', 'name', 'geometry_orig', 'geometry_final')

    def clean_geometry_orig(self):
        data = self.cleaned_data['geometry_orig']
        return self.transform(data)

    def clean_geometry_final(self):
        data = self.cleaned_data['geometry_final']
        return self.transform(data)

    def transform(self, wkt):
        geo = fromstr(wkt, srid=GEOMETRY_CLIENT_SRID)
        geo.transform(GEOMETRY_DB_SRID)
        return geo.ewkt
