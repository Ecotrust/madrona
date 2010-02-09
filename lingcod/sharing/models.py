from django.contrib.gis.db import models
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings


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
    shared_content_type = models.ForeignKey(ContentType,related_name="shared_content_type")
    container_content_type = models.ForeignKey(ContentType,blank=True,null=True,verbose_name="Content type of objects to serve as a 'container' for this type")
    container_set_property = models.CharField(max_length=40,blank=True,null=True,verbose_name="Property on the container object which returns a queryset of this type")

def get_shareables():
    """
    Introspects the current project and looks for 
    * a can_share* permission and its associated model name
    * if the model is a registered ShareableContent instance
    * whether those models have a user field (fk to auth Users)
    * whether those models have a sharing_groups ManyToMany field 
    * whether those model managers implement the all_for_user() method (ie the ShareableGeoManager)

    returns dict of models and their associated sharing permission 
     i.e. {'mlpampa': (<MplaMpa model class>, <CanShareMpa permission instance>) }
    """
    perms = Permission.objects.filter(codename__startswith="can_share")
    shareable = {}
    entries = ShareableContent.objects.all()
    registered_shareable = [x.shared_content_type for x in entries]
    for p in perms:
        model_class = p.content_type.model_class()
        # MP TODO this checks if field exists but need to do more robust checking on what type of field, where the fk points, etc
        if p.content_type in registered_shareable and \
           model_class.__dict__.has_key('sharing_groups') and \
           model_class.__dict__.has_key('user') and \
           model_class.__dict__['user'].__class__.__name__ == 'ReverseSingleRelatedObjectDescriptor' and \
           model_class.__dict__['sharing_groups'].__class__.__name__ == 'ReverseManyRelatedObjectsDescriptor':
            try:
                assert model_class.objects.shared_with_user
                shareable[p.content_type.model] = (model_class, p)
            except:
                pass
    return shareable

class SharingError(Exception):
    pass

        
def share_object_with_group(the_object, the_group):
    """
    The entry point for sharing a 'shareable' object with a group
    * Checks that the user has can_share_whatever permissions
    * Checks that the group to be shared with has the can_share_whatever permissions 
    * Sets 'sharing_group' field
    """
    # See if it's shareable and what the appropos permissions are
    shareables = get_shareables()
    try:
        model_class, permission = shareables[the_object.__class__.__name__.lower()]
    except:
        raise SharingError("This object is not shareable")
    perm_label = ".".join([model_class._meta.app_label,permission.codename])

    # Check that the user is of a group which can share 
    if not the_object.user.has_perm(perm_label):
        raise SharingError("You don't have permission to share this type of object") 

    # Check that the group to be shared with has appropos permissions
    try:
        the_group.permissions.get(id=permission.id)
    except:
        raise SharingError("The group you are trying to share with does not have can_share permissions")

    # do it
    the_object.sharing_groups.add(the_group)
    the_object.save()


def get_content_type_id(model_class):
    """
    Returns the content type primnary key for a given model class
    """
    try:
        return ContentType.objects.get(app_label=model_class._meta.app_label, model=model_class.__name__.lower()).id
    except:
        raise SharingError("Cannot get content type for %s " % model_class)


def share_object_with_groups(the_object, the_group_ids):
    """
    Shares the given object exclusively to the specified groups
    all other groups will be wiped
    """
    # See if it's shareable and what the appropos permissions are
    shareables = get_shareables()
    try:
        model_class, permission = shareables[the_object.__class__.__name__.lower()]
    except:
        raise SharingError("This object is not shareable")
    perm_label = ".".join([model_class._meta.app_label,permission.codename])

    # Check that the user is of a group which can share 
    if not the_object.user.has_perm(perm_label):
        raise SharingError("You don't have permission to share this type of object") 

    # if empty list for group ids, just wipe the slate clean and return
    if len(the_group_ids) == 0:
        the_object.sharing_groups.clear()
        the_object.save()
        return

    # If we have some groups share with, try it
    try:
        groups = Group.objects.filter(pk__in=the_group_ids)
    except:
        raise SharingError("No groups with those ids")

    the_object.sharing_groups.clear()
    for g in groups:
        # Check that the group to be shared with has appropos permissions
        try:
            g.permissions.get(id=permission.id)
        except:
            raise SharingError("The group you are trying to share with does not have can_share permissions")

        the_object.sharing_groups.add(g)

    the_object.save()

def groups_users_sharing_with(user, include_public=False):
    """
    Get a dict of groups and users that are currently sharing items with a given user
    returns something like {'our_group': {'group': <Group our_group>, 'users': [<user1>, <user2>,...]}, ... }
    """
    shareables = get_shareables()
    groups_sharing = {}
    for s in shareables.keys():
        model_class = shareables[s][0]
        permission = shareables[s][1]
        shared_objects = model_class.objects.shared_with_user(user)
        for group in user.groups.all():
            # Unless overridden, public shares don't show up here
            if group.name in settings.SHARING_TO_PUBLIC_GROUPS and not include_public:
                continue
            # User has to be staff to see these
            if group.name in settings.SHARING_TO_STAFF_GROUPS and not user.is_staff:
                continue
            group_objects = shared_objects.filter(sharing_groups=group)
            user_list = []
            for gobj in group_objects:
                if gobj.user not in user_list and gobj.user != user:
                    user_list.append(gobj.user)
            if len(user_list) > 0:
                if group.name in groups_sharing.keys():
                    groups_sharing[group.name]['users'].extend(user_list)
                else:
                    groups_sharing[group.name]={'group':group, 'users': user_list}
            print group, user_list
    print groups_sharing
    if len(groups_sharing.keys()) > 0:
        return groups_sharing
    else:
        return None

