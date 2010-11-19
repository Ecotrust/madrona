from django.db import models
from django.contrib.gis.db import models


class BaseManipulatorGeometryManager(models.GeoManager):
    """Returns the currently active data layer (determined by the active attribute).
    """
    def current(self):
        return self.get(active=True)

class BaseManipulatorGeometry(models.Model):
    """Abstract Model in which an inheriting subclass can be used for storing a data layer used by a Manipulator

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``creation_date``       When the layer was created. Is not changed on
                                updates.
                                
        ``active``              Whether this layer represents the current 
                                data layer. If set to true and and another
                                layer is active, that old layer will be 
                                deactivated.
        ======================  ==============================================
    """    
    creation_date = models.DateTimeField(auto_now=True) 
    
    active = models.BooleanField(default=True, help_text="""
        Checking here indicates that this layer list should be the one used in
        the application. Copies of other layer lists are retained in the
        system so you can go back to an old version if necessary.
    """)
    
    objects = BaseManipulatorGeometryManager()
    
    def save(self, *args, **kwargs):
        super(BaseManipulatorGeometry, self).save(*args, **kwargs)
        if self.active and self.__class__.objects.filter(active=True).count() > 1:
            # Ensure that any previously active layer is deactivated -- There can be only one!
            self.__class__.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
            
    class Meta:
        abstract = True

    