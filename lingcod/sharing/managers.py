from django.contrib.gis.db import models
from models import get_shareables, ShareableContent
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
            raise NotImplementedError("%s uses ShareableGeoManager but lacks a ManyToMany field 'sharing_groups',is not registered with ShareableContent, or lacks 'can_share*' permissions." % self.model.__name__)

        app_name = self.model._meta.app_label
        model_name = self.model.__name__.lower()
        model_class, permission = shareables[model_name]

        # Check for a Container 
        shared_content_type = permission.content_type.shared_content_type.all()[0] 
        if shared_content_type.container_content_type and shared_content_type.container_set_property:
            # Get container objects shared with user
            shared_containers = shared_content_type.container_content_type.model_class().objects.shared_with_user(user)
            # Create list of contained object ids
            contained_ids = []
            for sc in shared_containers:
                contained = sc.__getattribute__(shared_content_type.container_set_property)
                contained_ids.extend([x.id for x in contained])

            return self.filter(
                models.Q(
                    sharing_groups__permissions__codename=permission.codename, 
                    sharing_groups__in=user.groups.all(),
                    sharing_groups__permissions__content_type__app_label=app_name
                ) | 
                models.Q(
                    pk__in=contained_ids
                )
            ).distinct()
        else:     
            # No containers, just a straight 'is it shared' query
            return self.filter(
                models.Q(
                    sharing_groups__permissions__codename=permission.codename, 
                    sharing_groups__in=user.groups.all(),
                    sharing_groups__permissions__content_type__app_label=app_name
                )
            ).distinct()
