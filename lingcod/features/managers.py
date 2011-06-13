from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group, Permission
from django.conf import settings
from lingcod.features import registered_models

class ShareableGeoManager(models.GeoManager):
    def shared_with_user(self, user, filter_groups=None, exclude_models=None):
        """
        Returns a queryset containing any objects that have been 
        shared with a group the user belongs to.
        
        Assumes that the model has been setup according to the instructions
        for implementing a shared model.
        """
        app_name = self.model._meta.app_label
        model_name = self.model.__name__.lower()
        perm = Permission.objects.get(codename='can_share_features')

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
        potential_parents = self.model.get_options().get_potential_parents()
        if potential_parents:
            contained_ids = []
            for collection_model in potential_parents:
                # Avoid infinite recursion
                if exclude_models and collection_model in exclude_models:
                    continue
                
                exclude_models = None
                if collection_model == self.model:
                    # On the next recurisive go-round, avoid infinite recursion
                    exclude_models = [self.model]

                # Get container objects shared with user
                if filter_groups:
                    shared_containers = collection_model.objects.shared_with_user(user,filter_groups=filter_groups,exclude_models=exclude_models)
                else:
                    shared_containers = collection_model.objects.shared_with_user(user,exclude_models=exclude_models)

                # Create list of contained object ids
                for sc in shared_containers:
                    #contained = sc.__getattribute__(shared_content_type.container_set_property)
                    contained = sc.feature_set(recurse=True,feature_classes=[self.model])
                    contained_ids.extend([x.id for x in contained])
           
            return self.filter(
                models.Q(
                    sharing_groups__permissions=perm, 
                    sharing_groups__in=groups
                ) | 
                models.Q(
                    pk__in=contained_ids
                )
            ).distinct()
        else:     
            # No containers, just a straight 'is it shared' query
            return self.filter(
                models.Q(
                    sharing_groups__permissions=perm, 
                    sharing_groups__in=groups
                )
            ).distinct()
