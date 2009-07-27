from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings

from managers import *

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

        ``editable``            Whether or not the MPA can modified.
        
        ``geometry_orig``       PolygonField representing the MPA boundary as
                                originally drawn by the user
        
        ``geometry_final``      PolygonField representing the MPA boundary
                                after postprocessing.
        ======================  ==============================================
"""   
    user = models.ForeignKey(User)
    name = models.TextField(verbose_name="MPA Name")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    editable = models.NullBooleanField(default=True,null=True, blank=True, editable=False)
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Original MPA boundary")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID,null=True, blank=True, verbose_name="Final MPA boundary")   
    objects = MpaManager()
    
    class Meta:
        abstract=True
