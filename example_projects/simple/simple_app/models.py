from django.contrib.gis.db import models
from lingcod.mpa.models import Mpa
from manipulators import *
from lingcod.manipulators.manipulators import *

class Mpa(models.Model):
    """Model used for representing marine protected areas or MPAs

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``name``                Name of the MPA
                                
        ``date_created``        When the MPA was created. Is not changed on
                                updates.
        ``date_modified``       When the MPA geometry was last updated.

        ``editable``            Whether or not the MPA can modified.
        
        ``geometry_orig``       PolygonField representing the MPA boundary as
                                originally drawn by the user
        
        ``geometry_final``      PolygonField representing the MPA boundary
                                after postprocessing.
        ======================  ==============================================
    """   
    name = models.TextField(verbose_name="MPA Name")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    editable = models.NullBooleanField(default=True,null=True, blank=True, editable=False)
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Original MPA boundary")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Final MPA boundary")   
    
    class Meta:
        abstract=True

    class Options:
        #manipulators = [ ClipToStudyRegionManipulator, ClipToGraticuleManipulator, ClipToEstuariesManipulator ]
        manipulators = [ ClipToStudyRegionManipulator ]
        #manipulators = [ ClipToEstuariesManipulator ]
        #manipulators = [ ClipToShapeManipulator ]
        #manipulators = [ ClipToGraticuleManipulator ]
        
    def __str__(self):
        return self.name

#THE FOLLOWING ESTUARIES RELATED CLASSES ARE INCOMPLETE AND HAVE BEEN ADDED HERE FOR TESTING PURPOSES!!!
class EstuariesManager(models.GeoManager):
    def current(self):
        return self.all()
        
class Estuaries(models.Model):
    """Model used for representing Estuaries

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the Estuary
                                
        ``geometry``            PolygonField representing the Estuary boundary
                                
        ======================  ==============================================
    """   
    name = models.TextField(verbose_name="Estuary Name")
    
    geometry = models.MultiPolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Estuary boundary")
       
    objects = EstuariesManager()
    
    class Meta:
        db_table = u'mm_estuaries' 