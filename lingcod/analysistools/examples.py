from models import Analysis
from django.contrib.gis.db import models
from django.conf import settings
from lingcod.features.models import Feature, FeatureForm, get_absolute_media_url
from lingcod.common.utils import get_class
from lingcod.features import register
from django.contrib.gis.geos import GEOSGeometry 
from lingcod.common.utils import asKml
from django import forms
from widgets import SliderWidget
import os

@register
class BufferPoint(Analysis):
    input_lat = models.FloatField(verbose_name='Latitude')
    input_lon = models.FloatField(verbose_name='Longitude') 
    input_buffer_distance = models.FloatField(verbose_name="Buffer Distance (m)")

    # All output fields should be allowed to be Null/Blank
    output_area= models.FloatField(null=True,blank=True, 
            verbose_name="Buffer Area (meters)")
    output_point_geom = models.PointField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Point Geometry")
    output_poly_geom = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Buffered Point Geometry")

    def run(self):
        try:
            g = GEOSGeometry('SRID=4326;POINT(%s %s)' % (self.input_lon, self.input_lat))
            g.transform(settings.GEOMETRY_DB_SRID)
            self.output_point_geom = g
            self.output_poly_geom = g.buffer(self.input_buffer_distance)
            self.output_area = self.output_poly_geom.area
        except:
            return False
        return True

    @property 
    def kml_done(self):
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s</name>
            <styleUrl>#%s-default</styleUrl>
            <MultiGeometry>
            %s
            %s
            </MultiGeometry>
        </Placemark>
        """ % (self.uid, self.name, self.model_uid(),
            asKml(self.output_point_geom.transform(
                    settings.GEOMETRY_CLIENT_SRID, clone=True)),
            asKml(self.output_poly_geom.transform(
                    settings.GEOMETRY_CLIENT_SRID, clone=True)))

    @property 
    def kml_working(self):
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s (WORKING)</name>
            <styleUrl>#%s-default</styleUrl>
            <Point>
              <coordinates>%s,%s</coordinates>
            </Point>
        </Placemark>
        """ % (self.uid, self.name, self.model_uid(), 
                self.input_lon, self.input_lat)

    @property
    def kml_style(self):
        return """
        <Style id="%s-default">
            <IconStyle>
                <color>ffffffff</color>
                <colorMode>normal</colorMode>
                <scale>0.9</scale> 
                <Icon> <href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href> </Icon>
            </IconStyle>
            <LabelStyle>
                <color>ffffffff</color>
                <scale>0.8</scale>
            </LabelStyle>
            <PolyStyle>
                <color>778B1A55</color>
            </PolyStyle>
        </Style>
        """ % (self.model_uid(),)

    class Options:
        form = 'lingcod.analysistools.models.BufferPointsForm'
        show_template = 'analysis/show.html'

#from django.forms.models import modelform_factory
#exclude_fieldnames = list(FeatureForm.Meta.exclude)
#for f in BufferPoint.output_fields():
#    exclude_fieldnames.append(f.attname)
#BufferPointsForm = modelform_factory(model=BufferPoint,
#        form=FeatureForm,
#        exclude=exclude_fieldnames)

class BufferPointsForm(FeatureForm):
    input_lat = forms.FloatField(max_value=90, min_value=-90, label="Latitude")
    input_lon = forms.FloatField(max_value=180, min_value=-180, label="Longitude")
    input_buffer_distance = forms.FloatField(widget=SliderWidget(min=0.0001, max=10000),
            label = "Buffer Distance (m)",
            min_value=0.0001, max_value=10000)

    class Meta(FeatureForm.Meta):
        # TODO put all this in AnalysisForm and inherit
        # requires lots of Metaprogramming complexity
        model = BufferPoint
        exclude = list(FeatureForm.Meta.exclude)
        for f in BufferPoint.output_fields():
            exclude.append(f.attname)

