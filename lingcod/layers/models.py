from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from lingcod.features.managers import ShareableGeoManager
from lingcod.features.models import Feature, FeatureForm
from django.core.urlresolvers import reverse
import os

class PrivateLayerList(Feature):
    """
    Abstract Model for storing uploaded restricted-access kml files
    Owned by a single user, can be shared with any group(s) 
    that the owner is a member of (assuming group has
    can_share_features permissions)
    """
    priority = models.FloatField(help_text="Floating point. Higher number = appears higher up on the KML tree.",default=0.0)
    kml_file = models.FileField(upload_to='upload/private-kml-layers/%Y/%m/%d', help_text="""
        KML or KMZ file. Can use NetworkLinks pointing to remote kml datasets or WMS servers.
    """, blank=False, max_length=510)

    @property
    def kml(self):
        return ""

    @property
    def kml_style(self):
        return ""

    @property
    def kml_full(self):
        try:
            f = self.kml_file.read()
            return f
        except:
            return """<kml xmlns="http://www.opengis.net/kml/2.2"><Document></Document></kml>"""

    class Meta:
        abstract=True

class PrivateSuperOverlay(Feature):
    """
    Abstract Model for presenting restricted-access multi-file kml trees on disk
    Owned by a single user, can be shared with any group(s) 
    that the owner is a member of (assuming group has
    can_share_features permissions)
    """
    priority = models.FloatField(help_text="Floating point. Higher number = appears higher up on the KML tree.",default=0.0)
    base_kml = models.FilePathField(path=settings.SUPEROVERLAY_ROOT, match="^doc.kml$", recursive=True, help_text="""
        Base KML file of the superoverlay. Must be called 'doc.kml'. This file (and all subsequent files in the tree) must use
        relative paths.  The user making the request only needs permissions for the base kml. 
        IMPORTANT: Every file in and below the base kml's directory path is accessible 
        if the user has proper permissions on the base kml.""")

    @property
    def kml(self):
        return ""

    @property
    def kml_style(self):
        return ""

    @property
    def kml_full(self):
        return self.base_kml.read()

    class Meta:
        abstract=True

    def save(self, *args, **kwargs):
        if self.base_kml == os.path.join(settings.SUPEROVERLAY_ROOT, 'doc.kml'):
            raise Exception("We don't allow /doc.kml at the SUPEROVERLAY_ROOT dir... security risk.")
        else:
            super(PrivateSuperOverlay, self).save(*args, **kwargs)


class PublicLayerList(models.Model):
    """Model used for storing uploaded kml files that list all public layers.

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``active``              Whether this kml file represents the currently 
                                displayed data layers. If set to true and 
                                another ``PublicLayerList`` is active, that 
                                old list will be deactivated.

        ``kml_file``            Django `FileField <http://docs.djangoproject.com/en/dev/ref/models/fields/#filefield>`_
                                that references the actual kml
                                
        ``creation_date``       When the layer was created. Is not changed on
                                updates.
        ======================  ==============================================
"""    
    
    creation_date = models.DateTimeField(auto_now=True) 
    
    active = models.BooleanField(default=True, help_text="""
        Checking here indicates that this layer list should be the one used in
        the application. Copies of other layer lists are retained in the
        system so you can go back to an old version if necessary.
    """)
    
    kml_file = models.FileField(upload_to='layers/uploaded-kml/', help_text="""
        KML file that represents the public layers list. This file can use
        NetworkLinks pointing to remote kml datasets or WMS servers.
        For more information on how to create this kml file see the 
        documentation.
    """, blank=False, max_length=510)
    
    def __unicode__(self):
        return "PublicLayerList, created: %s" % (self.creation_date)
    
    def save(self, *args, **kwargs):
        super(PublicLayerList, self).save(*args, **kwargs)
        if self.active and PublicLayerList.objects.filter(active=True).count() > 1:
            # Ensure that any previously active layer is deactivated
            # There can be only one!
            PublicLayerList.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
            
