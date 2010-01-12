from django.contrib.gis.db import models
from django.conf import settings

class BioregionManager(models.GeoManager):
    def which_bioregion(self,geom):
        """Given a geometry, this method will return the name of the bioregion that contains that geometry's centroid."""
        pnt = geom.centroid
        qs = super(BioregionManager,self).get_query_set().filter(geometry__contains=pnt)
        if qs.count() > 1:
            raise Exception('The submitted geometry has a centroid that is in more than one bioregion. Either there is something wrong with the bioregions geometry or the fabric of the universe has been torn.')
        elif qs.count() < 1:
            return None
        else:
            return qs[0]

class Bioregion(models.Model):
    """Model used for representing bioregions.  Bioregions are biologically significant
       subdivisions of study regions.  MLPA reports are often broken down by bioregion so
       we need to be able to determine which bioregion each MPA falls within.  The bioregions
       will be represented as very generalized polygons that overshoot the study region considerably.
       This way, most modifications to the study region will not require changes to the bioregions.
       Additionally, having few verticies will speed up any spatial operations with the bioregions.

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================

        ``name``                Name of the bioregion
                                
        ``creation_date``       Automatically assigned

        ``modification_date``   Automatically assigned
                                
        ``geometry``            PolygonField representing the bioregion boundary
                                
        ======================  ==============================================
"""   
    name = models.CharField(verbose_name="Study Region Name", max_length=255, null=True, blank=True)   
    creation_date = models.DateTimeField(auto_now_add=True) 
    modification_date = models.DateTimeField(auto_now=True)     
    geometry = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Study region boundary")
    objects = BioregionManager()
    
    def __unicode__(self):
        """docstring for __unicode__"""
        return self.name
        
