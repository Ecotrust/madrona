from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from lingcod.features.managers import ShareableGeoManager
from lingcod.features.models import Feature, FeatureForm
from lingcod.common.utils import get_logger
from django.core.urlresolvers import reverse
from django.utils.encoding import DjangoUnicodeDecodeError
import os

logger = get_logger()

class UserUploadedKml(Feature):
    """
    Abstract Model for storing uploaded restricted-access kml files

    Owned by a single user, can be shared with any group(s) 
    that the owner is a member of (assuming group has
    can_share_features permissions)

    These are features and will show up in the MyShapes/SharedShapes panels
    """
    kml_file = models.FileField(upload_to='upload/private-kml-layers/%Y/%m/%d', help_text="""
        KML or KMZ file. Can use NetworkLinks pointing to remote kml datasets or WMS servers.
    """, blank=False, max_length=510)
    description = models.TextField(default="", null=True, blank=True)

    @property
    def basename(self):
        """
        Name of the file itself without the path
        """
        return os.path.basename(self.kml_file.path)

    @property
    def kml(self):
        return "<!-- no kml representation, use network link to kml-file url -->"

    @classmethod
    def css(klass):
        return """ li.%s > .icon { 
        background: url('%scommon/images/kml_document_icon.png') no-repeat 0 0 ! important; 
        } """ % (klass.model_uid(), settings.MEDIA_URL)

    @property
    def kml_style(self):
        return """
        <Style id="%(model_uid)s-default">
        </Style>
        """ % {'model_uid': self.model_uid()}

    @property
    def kml_style_id(self):
        return "%s-default" % self.model_uid()

    @property
    def kml_full(self):
        from django.utils.encoding import smart_unicode
        f = self.kml_file.read()
        try:
            return smart_unicode(f)
        except DjangoUnicodeDecodeError:
            # probably a binary kmz
            return f
        except:
            logger.warn("%s.kml_full is failing .. returning an empty kml doc" % self)
            return """<kml xmlns="http://www.opengis.net/kml/2.2"><Document></Document></kml>"""

    class Meta:
        abstract=True

class PrivateKml(models.Model):
    """
    For presenting restricted-access KML datasets that don't belong to a particular user
    These can be either:
     * multi-file kml trees on disk (ie superoverlays)
     * single kml/kmz files 

    Note that this is NOT a Feature so it doesn't have any of the sharing API, wont show in myshapes, etc

    Admin must upload data to server and place in settings.PRIVATE_KML_ROOT

    VERY IMPORTANT SECURITY CONSIDERATIONS...
     * PRIVATE_KML_ROOT should not be web accessible!
     * Each PrivateKml should have it's own subdirectory in PRIVATE_KML_ROOT!
       THIS IS IMPORTANT; Every file in and below the base kml's directory path is accessible 
       if the user has proper permissions on the base kml.

    Sharing and permissions must be implemented one-off in the views using the
    sharing_groups many-to-many field. 
    """
    priority = models.FloatField(help_text="Floating point. Higher number = appears higher up on the KML tree.",
            default=0.0)
    name = models.CharField(verbose_name="Name", max_length="255",unique=True)
    sharing_groups = models.ManyToManyField(Group,blank=True,null=True,
            verbose_name="Share layer with the following groups")
    base_kml = models.FilePathField(path=settings.PRIVATE_KML_ROOT, match=".kml$", 
        recursive=True, 
        help_text="""
        Path to KML file.
        If a superoverlay tree, use relative paths.  
        The user making the request only needs permissions for the base kml. 
        IMPORTANT: Every file in and below the base kml's directory path is accessible 
        if the user has proper permissions on the base kml.""")

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
            


class PrivateLayerList(UserUploadedKml):
    """
    Note: This is just a wrapper to avoid breaking 
    old code that relies on this class name
    """
    class Meta:
        abstract=True
