from django import forms
#from django.contrib.admin.helpers import AdminForm
from lingcod.intersection.models import *
from django.contrib.gis.admin import GeoModelAdmin, site as admin_site

        
class SplitToSingleFeaturesForm(forms.Form):
    def __init__(self, initial_pk, *args, **kwargs):
        super(SplitToSingleFeaturesForm, self).__init__(*args, **kwargs)
        self.fields['mfshp_pk'].initial = initial_pk
        self.fields['shp_field'].choices = [('', '----------')] + [(str(sf.name), sf.name + ' (' + str(sf.distinct_values) + ')') for sf in MultiFeatureShapefile.objects.get(pk=initial_pk).shapefilefield_set.all().order_by('distinct_values')]
    mfshp_pk = forms.IntegerField(widget=forms.HiddenInput)
    shp_field = forms.ChoiceField(label='Shape file field to split on (# of distinct values in field)')

class PolyAdmin(GeoModelAdmin):
    pass

admin_instance = PolyAdmin(TestPolygon, admin_site)
poly_field = TestPolygon._meta.get_field('geometry')
admin_instance.default_lat = 33.5
admin_instance.default_lon = -119
admin_instance.default_zoom = 7
admin_instance.display_wkt = True
PolygonWidget = admin_instance.get_map_widget(poly_field)


class TestIntersectionForm(forms.ModelForm):
    OrganizationScheme_Choices = [('None', 'Default')]
    [OrganizationScheme_Choices.append((osc.pk,osc.name)) for osc in OrganizationScheme.objects.all()]
    org_scheme = forms.ChoiceField(choices=OrganizationScheme_Choices)
    FormatChoices = [('html', 'HTML'), ('csv', 'CSV'), ('json','JSON')]
    format = forms.ChoiceField(choices=FormatChoices)
    geometry = forms.CharField(widget=PolygonWidget() )
    class Meta:
        model = TestPolygon
    class Media:
        js = ("http://openlayers.org/api/2.6/OpenLayers.js",)
        
class TestPolygonIntersectionForm(forms.ModelForm):
    OrganizationScheme_Choices = [('None', 'Default')]
    [OrganizationScheme_Choices.append((osc.pk,osc.name)) for osc in OrganizationScheme.objects.all()]
    org_scheme = forms.ChoiceField(choices=OrganizationScheme_Choices)
    FormatChoices = [('html', 'HTML'), ('csv', 'CSV'), ('json','JSON')]
    format = forms.ChoiceField(choices=FormatChoices)
    TestPoly_Choices = [(tp.geometry.wkt,tp.pk) for tp in TestPolygon.objects.all()]
    geometry = forms.ChoiceField(choices=TestPoly_Choices)
    class Meta:
        model = TestPolygon
    class Media:
        js = ("http://openlayers.org/api/2.6/OpenLayers.js",)
