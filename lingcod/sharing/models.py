from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType

class ShareableContent(models.Model):
    """
    Defines which objects are shareable and some details about their behavior
    
    ======================  ==============================================
    Attribute               Description
    ======================  ==============================================
    ``shared_content_type``     Content type (fk) of the model to be shared

    ``container_content_type``  Type to serve as container 

    ``container_set_property``  Property on the container model to return
                                a queryset of the associated content types

    ======================  ==============================================
    """ 
    def __unicode__(self):
        return u'%s' % self.shared_content_type

    shared_content_type = models.ForeignKey(ContentType,related_name="shared_content_type")
    container_content_type = models.ForeignKey(ContentType,blank=True,null=True,verbose_name="Content type of objects to serve as a 'container' for this type")
    container_set_property = models.CharField(max_length=40,blank=True,null=True,verbose_name="Property on the container object which returns a queryset of this type")


class NotShareable(Exception):
    pass

class SharingError(Exception):
    pass

