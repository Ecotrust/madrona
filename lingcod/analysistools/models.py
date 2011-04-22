from django.contrib.gis.db import models
from django.conf import settings
from lingcod.features.models import Feature, FeatureForm, get_absolute_media_url
from lingcod.common.utils import get_class
from lingcod.features import register
from django.contrib.gis.geos import GEOSGeometry 
from lingcod.common.utils import asKml
import os

class Analysis(Feature):
    """
    Abstract Feature model representing the inputs and outputs
    of an analysis or modeling run 
    """

    @property
    def kml(self):
        if self.done:
            return self.kml_done
        else:
            return self.kml_working

    @property
    def kml_done(self):
        """
        Translate the model outputs to KML
        """
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s</name>
        </Placemark>
        """ % (self.uid, self.name)

    @property
    def kml_working(self):
        """
        Translate the model outputs to KML
        """
        return """
        <Placemark id="%s">
            <visibility>0</visibility>
            <name>%s (Working...)</name>
        </Placemark>
        """ % (self.uid, self.name)

    @property
    def kml_style(self):
        return ""

    @classmethod
    def input_fields(klass):
        return [f for f in klass._meta.fields if f.attname.startswith('input_')]

    @property
    def inputs(self):
        """
        Returns a dict of all input parameters
        """
        odict = {}
        for f in self.input_fields():
            odict[f.verbose_name] = self._get_FIELD_display(f)
        return odict

    @classmethod
    def output_fields(klass):
        return [f for f in klass._meta.fields if f.attname.startswith('output_')]

    @property
    def outputs(self):
        """
        Returns a dict of all output parameters
        If processing is incomplete, values will be None
        """
        odict = {}
        for f in self.output_fields():
            odict[f.verbose_name] = self._get_FIELD_display(f)
        return odict

    @property
    def done(self):
        """
        If it's asynchronously processed, this is the definitive
        property to determine if processing is completed.
        """
        # For now just check that the outputs are not None
        for of in self.outputs.keys():
            if not self.outputs[of]:
                return False
        return True

    def run(self):
        """
        Method to execute the model. 
        Passes all input parameters to the analysis backend, 
        takes the results and stores in the model output fields. 
        """
        pass

    def save(self, *args, **kwargs):
        self.run()
        super(Feature, self).save(*args, **kwargs) # Call the "real" save() method

    class Meta:
        abstract = True
