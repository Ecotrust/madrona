from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.common.utils import LookAtKml
from lingcod.manipulators.manipulators import *
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class MpaDesignation(models.Model):
    """Model used to represent the designation of the MPA
        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``name``                Designation of the MPA

        ``acronym``             The acronym for this MPA designation

        ``poly_outline_color``  Hex Color for rendering the outline/border

        ``poly_fill_color``     Hex Color for rendering the polygon area
        ======================  ==============================================
    """
    name = models.TextField(verbose_name="Designation Name")
    acronym = models.CharField(max_length=10, unique=True, verbose_name="Designation Acronym")
    poly_outline_color = models.CharField(max_length=8, default="ffffffff", verbose_name="Hex Color for rendering outline/border")
    poly_fill_color = models.CharField(max_length=8, default="ff0000ff", verbose_name="Hex Color for rendering polygon area")
    url = models.URLField(verify_exists=False,verbose_name="URL to more info on this MPA Designation")

    def __unicode__(self):
        return "(%s) %s" % (self.acronym, self.name)

class Mpa(models.Model):
    """Model used for representing marine protected areas or MPAs

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Owner of the MPA

        ``name``                Name of the MPA
                                
        ``date_created``        When the MPA was created. Is not changed on
                                updates.
        ``date_modified``       When the MPA geometry was last updated.
        
        ``geometry_orig``       PolygonField representing the MPA boundary as
                                originally drawn by the user
        
        ``geometry_final``      PolygonField representing the MPA boundary
                                after postprocessing.
                                
        ``content_type``        Content type of the associated Array 
                                (Generic One-to-Many)
                                
        ``object_id``           pk of the specific array object
        
        ``array``               Use to access the associated Array (read-only)
        ======================  ==============================================
    """   
    user = models.ForeignKey(User)
    name = models.TextField(verbose_name="MPA Name")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Original MPA boundary")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Final MPA boundary")
    
    # Array relation fields
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True,null=True)
    array = generic.GenericForeignKey('content_type', 'object_id')
    
    designation = models.ForeignKey(MpaDesignation)

    objects = models.GeoManager()
    
    class Meta:
        abstract=True
        
    class Options:
        manipulators = [ ClipToStudyRegionManipulator ]  

    def __unicode__(self):
        return self.name
        
    def geom_as_kml(self):
        """
        returns the final geometry as a kml geometry string projected into wgs84
        """
        wgs84_geom = self.geometry_final.transform(4326, clone=True)
        return wgs84_geom.kml

    def lookAtKml(self):
        """
        Get the kml for a camera perspective looking at the MPA's final geometry
        """
        return LookAtKml( self.geometry_final )
    
    
    def kmlOrigGeom(self, style_domain):
        self.geometry_orig.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' original geometry</name>' + self.kmlOrigGeomStyle(style_domain) + LookAtKml( self.geometry_orig ) + self.geometry_orig.kml + '</Placemark>'
    
    def kmlFinalGeom(self, style_domain):
        self.geometry_final.transform(4326)
        return '<Placemark>' + '<name>' + self.name + ' final geometry</name>' + self.kmlFinalGeomStyle(style_domain) + LookAtKml( self.geometry_final ) + self.geometry_final.kml + '</Placemark>'
        
    
    def kmlOrigGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ffffff</color> </PolyStyle></Style>'
    
    
    def kmlFinalGeomStyle(self, style_domain):
        return '<Style> <LineStyle> <color>ffffffff</color> <width>2</width> </LineStyle> <PolyStyle> <color>80ff0000</color> </PolyStyle></Style>'
        
        
    def kmlFolder(self, style_domain):
        """
        Return a kml folder containing the kml for this mpa's final and orginal geometry
        """
        return '<Document><name>MPAs</name><Folder>' + '<name>' + self.name + '</name>' + self.kmlFinalGeom(style_domain) + self.kmlOrigGeom(style_domain) + '</Folder></Document>'

    def add_to_array(self, array):
        """Adds the MPA to the specified array."""
        self.array = array
        self.save()
        
    def remove_from_array(self):
        """Sets the MPA's `array` property to None."""
        self.array = None
        self.save()
