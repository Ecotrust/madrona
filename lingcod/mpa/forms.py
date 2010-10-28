from django.forms import ModelForm
from django import forms
from lingcod.mpa.models import *
from lingcod.mpa.models import Mpa
from lingcod.features.forms import FeatureForm as UserForm
from django.contrib.gis.gdal import OGRGeometry
from django.contrib.gis.geos import fromstr
from django.conf import settings
from settings import GEOMETRY_CLIENT_SRID, GEOMETRY_DB_SRID
from lingcod.manipulators.manipulators import display_kml
from django.utils.safestring import mark_safe

class LoadForm(ModelForm):
    name = forms.CharField(max_length=100)
   
    class Meta:
        model = Mpa
        fields = ('user', 'name')


class ShapeInput(forms.HiddenInput):
    def render(self, name, value, attrs=None):
        # if value:
        #     geo = fromstr(value)
        #     if geo.srid != GEOMETRY_CLIENT_SRID:
        #         geo.srid = GEOMETRY_DB_SRID
        #         geo.transform(GEOMETRY_CLIENT_SRID)
        #     value = geo.ewkt
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
            
        
class MpaForm(UserForm):
    geometry_orig = forms.CharField(widget=ShapeInput())
    geometry_final = forms.CharField(widget=ShapeInput(), required=False)