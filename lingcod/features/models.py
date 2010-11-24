from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.sharing.managers import ShareableGeoManager
from lingcod.features.forms import FeatureForm
from lingcod.features import FeatureOptions
from lingcod.common.utils import asKml
import re
from django.contrib.contenttypes.models import ContentType

class Feature(models.Model):
    """Model used for representing user-generated features

        ======================  ==============================================
        Attribute               Description
        ======================  ==============================================
        ``user``                Creator

        ``name``                Name of the object
                                
        ``date_created``        When it was created

        ``date_modified``       When it was last updated.
                                        
        ======================  ==============================================
    """   
    user = models.ForeignKey(User)
    name = models.CharField(verbose_name="Name", max_length="255")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")
    date_modified = models.DateTimeField(auto_now=True, verbose_name="Date Modified")
    # Expose sharing functionality
    sharing_groups = models.ManyToManyField(Group,editable=False,blank=True,null=True,verbose_name="Share with the following groups")
    
    objects = ShareableGeoManager()

    class Meta:
        abstract=True
    
    @property
    def kml(self):
        return asKml(self.geometry_final.transform(settings.GEOMETRY_CLIENT_SRID, clone=True))

    @models.permalink
    def get_absolute_url(self):
        return ('%s_resource' % (self.get_options().slug, ), (), {
            'pk': self.pk
        })
    
    @classmethod
    def get_options(klass):
        return FeatureOptions(klass)
    
    @classmethod
    def model_uid(klass):
        ct = ContentType.objects.get_for_model(klass)
        return "%s_%s" % (ct.app_label, ct.model)
        
    @property
    def uid(self):
        if not self.pk:
            raise Exception(
                'Trying to get uid for feature class that is not yet saved!')
        return "%s_%s" % (self.model_uid(), self.pk, )
    
    def copy(self, user=None):
        """
        Returns a copy of this feature, setting the user to the specified 
        owner. Copies many-to-many relations
        """
        # Took this code almost verbatim from the mpa model code.
        # TODO: Test if this method is robust, and evaluate alternatives like
        # that described in django ticket 4027
        # http://code.djangoproject.com/ticket/4027
        the_feature = self

        # Make an inventory of all many-to-many fields in the original feature
        m2m = {}
        for f in the_feature._meta.many_to_many:
            m2m[f.name] = the_feature.__getattribute__(f.name).all()

        # The black magic voodoo way, 
        # makes a copy but relies on this strange implementation detail of 
        # setting the pk & id to null 
        # An alternate, more explicit way, can be seen at:
        # http://blog.elsdoerfer.name/2008/09/09/making-a-copy-of-a-model-instance
        the_feature.pk = None
        the_feature.id = None
        the_feature.save()

        the_feature.name = the_feature.name + " (copy)"

        # Restore the many-to-many fields
        for fname in m2m.keys():
            for obj in m2m[fname]:
                the_feature.__getattribute__(fname).add(obj)
    
        # Reassign User
        the_feature.user = user
        the_feature.save()
        return the_feature

class PolygonFeature(Feature):
    """Model used for representing user-generated polygon features. 
       Inherits from Feature and adds geometry fields.
    """   
    geometry_orig = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Original Polygon Geometry")
    geometry_final = models.PolygonField(srid=settings.GEOMETRY_DB_SRID, null=True, blank=True, verbose_name="Final Polygon Geometry")
    
    @property
    def centroid_kml(self):
        geom = self.geometry_final.point_on_surface.transform(settings.GEOMETRY_CLIENT_SRID, clone=True)
        return geom.kml

    class Meta(Feature.Meta):
        abstract=True
