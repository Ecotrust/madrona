from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.sharing.managers import ShareableGeoManager
from lingcod.features.forms import FeatureForm
from lingcod.features import FeatureConfig
import re

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
    
    @models.permalink
    def get_absolute_url(self):
        return ('%s_resource' % (self.get_config().slug, ), (), {
            'pk': self.pk
        })
    
    @classmethod
    def get_config(klass):
        return FeatureConfig(klass)