from django.contrib.gis.db import models
from django import forms
from lingcod.features import register
from lingcod.features.models import PointFeature, LineFeature, PolygonFeature, FeatureCollection
from lingcod.layers.models import PrivateLayerList, PrivateSuperOverlay 
from lingcod.features.forms import FeatureForm, SpatialFeatureForm
from lingcod.analysistools.models import Analysis
from lingcod.analysistools.widgets import SimplePoint, SliderWidget
from django.conf import settings

DESIGNATION_CHOICES = (
    ('R', 'Horizontal Axis'), 
    ('P', 'Vertical Axis'),
)

###########################
@register
class WindEnergy(PolygonFeature):
    designation = models.CharField(max_length=1, choices=DESIGNATION_CHOICES)
    class Options:
        verbose_name = 'Proposed Wind Energy Site'
        form = 'mlpa.models.WindEnergyForm'
        manipulators = []
        
class WindEnergyForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = WindEnergy


###########################
@register
class Station(PointFeature):
    incident = models.CharField(max_length=100,default='')
    class Options:
        verbose_name = 'Transformer Station'
        form = 'mlpa.models.StationForm'

class StationForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = Station

###########################
@register
class Transmission(LineFeature):
    voltage = models.FloatField(null=True)
    class Options:
        verbose_name = 'Transmission Line'
        form = 'mlpa.models.TransmissionForm'

class TransmissionForm(SpatialFeatureForm):
    class Meta(SpatialFeatureForm.Meta):
        model = Transmission

###########################
@register
class Folder(FeatureCollection):
    class Options:
        form = 'mlpa.models.FolderForm'
        valid_children = ( 
                'mlpa.models.WindEnergy', 
                'mlpa.models.Pipeline', 
                'mlpa.models.Transmission', 
                'mlpa.models.UserKml', 
                'mlpa.models.Folder' 
        )

class FolderForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = Folder

###########################
@register
class UserKml(PrivateLayerList):
    class Options:
        verbose_name = 'Upload from Google Earth KML'
        form = 'mlpa.models.UserKmlForm'

class UserKmlForm(FeatureForm):
    class Meta(FeatureForm.Meta):
        model = UserKml

############################
@register
class PinnipedSite(Analysis):
    input_point = models.PointField(srid=settings.GEOMETRY_DB_SRID, verbose_name='Pinniped Haulout Location')
    input_buffer_distance = models.FloatField(verbose_name="Buffer Distance (m)")

    # All output fields should be allowed to be Null/Blank
    output_area= models.FloatField(null=True,blank=True, 
            verbose_name="Buffer Area (meters)")
    output_poly_geom = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,
            null=True, blank=True, verbose_name="Buffered Point Geometry")

    @classmethod
    def mapnik_geomfield(self):
        return "output_poly_geom"

    def run(self):
        try:
            self.output_poly_geom = self.input_point.buffer(self.input_buffer_distance)
            self.output_area = self.output_poly_geom.area
        except:
            return False
        return True

    @property 
    def kml_done(self):
        return """
        %s

        <Placemark id="%s">
            <visibility>1</visibility>
            <name>%s</name>
            <styleUrl>#%s-default</styleUrl>
            <MultiGeometry>
            %s
            %s
            </MultiGeometry>
        </Placemark>
        """ % (self.kml_style, self.uid, escape(self.name), self.model_uid(),
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
        """ % (self.uid, escape(self.name), self.model_uid(), 
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
        verbose_name = "Pinniped Haulout Site"
        form = 'mlpa.models.PinnipedSiteForm'
        show_template = 'analysis/show.html'
        icon_url = 'analysistools/img/buffer-16x16.png'


class PinnipedSiteForm(FeatureForm):
    input_point = forms.CharField(widget=SimplePoint(),
            label="Pinniped Haulout Location")
    input_buffer_distance = forms.FloatField(
            widget=SliderWidget(min=10, max=50000,step=1,
                image = 'analysistools/img/buffer.png' ),
            label = "Buffer Distance (m)",
            min_value=0.0001, max_value=50000)

    class Meta(FeatureForm.Meta):
        # TODO put all this in AnalysisForm and inherit
        # requires lots of Metaprogramming complexity
        model = PinnipedSite
        exclude = list(FeatureForm.Meta.exclude)
        for f in PinnipedSite.output_fields():
            exclude.append(f.attname)
