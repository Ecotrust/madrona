from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group
from django.conf import settings
from lingcod.sharing.managers import ShareableGeoManager
from lingcod import rest
from lingcod.features.forms import FeatureForm

class GeoQuerySetManager(ShareableGeoManager):
    """ 
    Used to extend the queryset manager; see http://simonwillison.net/2008/May/1/orm/
    """
    def get_query_set(self):
        return self.model.QuerySet(self.model)


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
    sharing_groups = models.ManyToManyField(Group,blank=True,null=True,verbose_name="Share this with the following groups")

    objects = GeoQuerySetManager()
    
    def verbose_name(self):
        """Returns a name to use when representing this feature class within 
        the user interface. Set this name on a model using Rest.verbose_name
        """
        return getattr(self.Rest, 'verbose_name', self.__class__.__name__)

    class Meta:
        abstract=True
    
    class Rest:
        share=False
                

# The following code would usually go in a project, I'm just screwing around 
# here

class Folder(Feature):

    class Rest():
        verbose_name = 'Folder'
        form = 'lingcod.features.models.FolderForm'

class FolderForm(FeatureForm):
    class Meta:
        model = Folder

rest.register(Folder)