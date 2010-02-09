from django.contrib.gis.db import models
from models import get_shareables, ShareableContent
from django.contrib.auth.models import User, Group, Permission
from django.conf import settings

class ShareableGeoManager(models.GeoManager):
    def shared_with_user(self, user, filter_groups=None):
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

        if user.is_anonymous() or not user.is_authenticated():
            # public users get special treatment -
            # ONLY get to see anything shared with a public group
            groups = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
        else: 
            if user.is_staff:
                # Staff users get their groups,plus 'shared_to_staff_groups',  plus public groups 
                groups = Group.objects.filter(
                            models.Q(
                                pk__in=[x.pk for x in user.groups.all()]
                            ) | 
                            models.Q(
                                name__in=settings.SHARING_TO_PUBLIC_GROUPS
                            ) | 
                            models.Q(
                                name__in=settings.SHARING_TO_STAFF_GROUPS
                            )
                        ).distinct()
            else:
                # Non-staff authenticated users get their groups plus public groups, MINUS shared_to_staff groups
                groups = Group.objects.filter(
                            models.Q(
                                pk__in=[x.pk for x in user.groups.all()]
                            ) | 
                            models.Q(
                                name__in=settings.SHARING_TO_PUBLIC_GROUPS
                            )
                        ).distinct().exclude(name__in=settings.SHARING_TO_STAFF_GROUPS)

        if filter_groups and len(filter_groups)>0:
            groups = groups.filter(pk__in=[x.pk for x in filter_groups])
        else:
            filter_groups = None

        # Check for a Container 
        shared_content_type = permission.content_type.shared_content_type.all()[0] 
        if shared_content_type.container_content_type and shared_content_type.container_set_property:
            # Get container objects shared with user
            if filter_groups:
                shared_containers = shared_content_type.container_content_type.model_class().objects.shared_with_user(user,filter_groups=filter_groups)
            else:
                shared_containers = shared_content_type.container_content_type.model_class().objects.shared_with_user(user)

            # Create list of contained object ids
            contained_ids = []
            for sc in shared_containers:
                contained = sc.__getattribute__(shared_content_type.container_set_property)
                # MP TODO this doesn't work as it write to the db, 
                # would be ideal to dynamically set sharing_groups on contained objects
                #for x in contained:
                #    for sg in sc.sharing_groups.all():
                #        x.sharing_groups.add(sg)
                contained_ids.extend([x.id for x in contained])
           
            return self.filter(
                models.Q(
                    sharing_groups__permissions__codename=permission.codename, 
                    sharing_groups__in=groups,
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
                    sharing_groups__in=groups,
                    sharing_groups__permissions__content_type__app_label=app_name
                )
            ).distinct()
