from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from lingcod.features.managers import ShareableGeoManager
from lingcod.features.models import Feature, FeatureForm
from lingcod.features import register
import os

class PrivateLayerListForm(FeatureForm):
    pass

class PrivateSuperOverlayForm(FeatureForm):
    pass

@register
class PrivateLayerList(Feature):
    """
    Model for storing uploaded restricted-access kml files
    Owned by a single user, can be shared with any group(s) 
    that the owner is a member of (assuming group has
    can_share_features permissions)
    """
    priority = models.FloatField(help_text="Floating point. Higher number = appears higher up on the KML tree.",default=0.0)
    kml = models.FileField(upload_to='upload/private-kml-layers/', help_text="""
        KML file (not publically available). This file can use
        NetworkLinks pointing to remote kml datasets or WMS servers.
    """, blank=False, max_length=510)

    class Options:
        verbose_name = 'Private Layer List'
        form = 'lingcod.layers.models.PrivateLayerListForm'
    
@register
class PrivateSuperOverlay(Feature):
    """
    Model for presenting restricted-access multi-file kml trees on disk
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

    class Options:
        verbose_name = 'Private SuperOverlay'
        form = 'lingcod.layers.models.PrivateSuperOverlayForm'

    def save(self, *args, **kwargs):
        if self.base_kml == os.path.join(settings.SUPEROVERLAY_ROOT, 'doc.kml'):
            raise Exception("We don't allow /doc.kml at the SUPEROVERLAY_ROOT dir... security risk.")
        else:
            super(PrivateSuperOverlay, self).save(*args, **kwargs)
            
class UserLayerList(models.Model):
    """Model used for storing uploaded kml files that list all public layers.

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``active``              Whether this kml file represents the currently 
                                displayed data layers. If set to true and 
                                another ``UserLayerList`` assigned to the same user
                                is active, that old list will be deactivated.

        ``user``                Many to many field representing the users assigned to this data layer
                                
        ``kml``                 Django `FileField <http://docs.djangoproject.com/en/dev/ref/models/fields/#filefield>`_
                                that references the actual kml
                                
        ``creation_date``       When the layer was created. Is not changed on
                                updates.
        ======================  ==============================================
"""    
    
    creation_date = models.DateTimeField(auto_now=True) 
    
    user = models.ManyToManyField(User, null=True, blank=True, verbose_name="Data Layer Users")
    
    active = models.BooleanField(default=True, help_text="""
        Checking here indicates that this layer list should be the one used in
        the application. Copies of other layer lists are retained in the
        system so you can go back to an old version if necessary.
    """)
    
    kml = models.FileField(upload_to='layers/uploaded-kml/', help_text="""
        KML file that represents the public layers list. This file can use
        NetworkLinks pointing to remote kml datasets or WMS servers.
        For more information on how to create this kml file see the 
        documentation.
    """, blank=False, max_length=510)
    
    def __unicode__(self):
        return "UserLayerList, created: %s" % (self.creation_date)
    
    #NOTE:  more work needs to be done here so that more than one user can have an active layer
    def save(self, *args, **kwargs):
        super(UserLayerList, self).save(*args, **kwargs)
        #if self.active and UserLayerList.objects.filter(active=True).count() > 1:
            # Ensure that any previously active layer is deactivated
            # There can be only one!
            #UserLayerList.objects.filter(active=True).exclude(pk=self.pk).update(active=False)
            
    class Meta:
        permissions = (
            ("view_userlayerlist", "Can view user layer list"),
        )


class PublicLayerList(models.Model):
    """Model used for storing uploaded kml files that list all public layers.

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``active``              Whether this kml file represents the currently 
                                displayed data layers. If set to true and 
                                another ``PublicLayerList`` is active, that 
                                old list will be deactivated.

        ``kml``                 Django `FileField <http://docs.djangoproject.com/en/dev/ref/models/fields/#filefield>`_
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
    
    kml = models.FileField(upload_to='layers/uploaded-kml/', help_text="""
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
            
