from django.contrib.gis.db import models
from models import get_shareables
from django.contrib.auth.models import User, Group, Permission

# TODO DOCUMENT!
class ShareableGeoManager(models.GeoManager):
    def shared_with_user(self, user):
        """
        Returns a queryset containing any objects that have been 
        shared with a group the user belongs to.
        
        Assumes that the model has been setup according to the instructions
        for implementing a shared model.
        """
        # throw an exception if this is not going to work
        shareables = get_shareables()
        if not shareables.has_key(self.model.__name__.lower()):
            raise NotImplementedError("%s uses ShareableGeoManager but lacks a ManyToMany field 'sharing_groups' or 'can_share*' permissions." % self.model.__name__)

        app_name = self.model._meta.app_label
        model_class, permission = shareables[self.model.__name__.lower()]

        return self.filter(
            models.Q(
                sharing_groups__permissions__codename=permission.codename, 
                sharing_groups__in=user.groups.all(),
                sharing_groups__permissions__content_type__app_label=app_name
            ) 
        ).distinct()
