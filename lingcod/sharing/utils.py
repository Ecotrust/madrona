from lingcod.sharing.models import ShareableContent, SharingError, NotShareable
from lingcod.common.utils import get_logger
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

logger = get_logger()

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
        if model_class and p.content_type in registered_shareable and \
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

def get_content_type(model_class):
    """
    Returns the content type object for a given model class
    """
    try:
        return ContentType.objects.get(app_label=model_class._meta.app_label, model=model_class.__name__.lower())
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

def groups_users_sharing_with(user, include_public=False, spatial_only=True):
    """
    Get a dict of groups and users that are currently sharing items with a given user
    If spatial_only is True, only models which inherit from the Feature class will be reflected here
    returns something like {'our_group': {'group': <Group our_group>, 'users': [<user1>, <user2>,...]}, ... }
    """
    shareables = get_shareables()
    groups_sharing = {}

    if spatial_only:
        classnames = []
        from lingcod.features import registered_models
        from lingcod.features.models import Feature        
        for s in shareables.keys():
            if issubclass(shareables[s][0],Feature):
                classnames.append(s)
    else:
        classnames = shareables.keys()

    for s in classnames:
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
                    for user in user_list:
                        if user not in groups_sharing[group.name]['users']:
                            groups_sharing[group.name]['users'].append(user)
                else:
                    groups_sharing[group.name]={'group':group, 'users': user_list}
    if len(groups_sharing.keys()) > 0:
        return groups_sharing
    else:
        return None

def get_viewable_object_or_respond(model_class, pk, user):
    """
    Gets a single instance of model_class
    if it doesnt exist or user can't access it,
    return 404 or 403
    """
    # Does it even exist?
    try:
        obj = model_class.objects.get(pk=pk)
    except:
        raise Http404

    obj = None
    try:
        # Next see if user owns it
        obj = model_class.objects.get(pk=pk, user=user)
    except:
        try: 
            # ... finally see if its shared with the user
            obj = model_class.objects.shared_with_user(user).get(pk=pk)
        except model_class.DoesNotExist:
            return HttpResponse("Access denied", status=403)

    return obj

def can_user_view(model_class, pk, user):
    """
    Shortcut to determine if a user has permissions to read an object
    Either needs to own it or have it shared with them.
    returns : Viewable(boolean), HttpResponse
    """
    # Does it even exist?
    try:
        obj = model_class.objects.get(pk=pk)
    except:
        return False, HttpResponse("Object does not exist", status=404)

    try:
        # Next see if user owns it
        obj = model_class.objects.get(pk=pk, user=user)
        return True, HttpResponse("Object owned by user",status=202)
    except:
        try: 
            # ... finally see if its shared with the user
            obj = model_class.objects.shared_with_user(user).get(pk=pk)
            return True, HttpResponse("Object shared with user",status=202)
        except model_class.DoesNotExist:
            return False, HttpResponse("Access denied",status=403)
        except NotShareable:
            return False, HttpResponse("Object is not shareable.", status=401) 
        except:
            return False, HttpResponse("Object permissions cannot be determined using can_user_view.", status=500) 

    return False, HttpResponse("Server Error in can_user_view", status=500) 

def user_sharing_groups(user):
    """
    Returns a list of groups that user is member of and 
    and group must have sharing permissions (on any object)  
    """
    sbs = get_shareables()
    perms = []
    for model in sbs.keys():
        perm = sbs[model][1]
        if perm not in perms:
            perms.append(perm)
    groups = user.groups.filter(permissions__in=perms).distinct()
    return groups

def validate_sharing(model):
    """
    Given a model class, will return True if the model has the prerequisites for sharing
    If not, an appropriate SharingError is raised
    """
    logger.debug('Validated sharing setup for %s' % (model.__name__,) )

    # Test for fields: user, sharing_groups
    fkfields = [m.name for m in model._meta.fields if m.__class__.__name__ == 'ForeignKey']
    if not 'user' in fkfields:
        raise SharingError("Feature does not contain a 'user' ForeignKey field")

    m2mfields = [m.name for m in model._meta.many_to_many]
    if not 'sharing_groups' in m2mfields:
        raise SharingError("Feature does not contain a 'sharing_groups' ManyToMany field")

    # Test for manager with shared_with_user() method
    if not hasattr(model.objects, 'shared_with_user'):
        raise SharingError("Model's object manager does not have a shared_with_user() method.")

    return True

def sharing_disable(mc):
    """
    Disable all sharing for a model
    """
    ct = ContentType.objects.get_for_model(mc)
    # Make sure Feature does NOT have can_share_* permission;
    codename = "can_share_%s" % mc._meta.module_name
    try:
        p = Permission.objects.get(codename=codename)
        logger.debug("Drop can_share Permissions for %r" % ct)
        p.delete()
    except Permission.DoesNotExist:
        pass
    # Make sure Feature does NOT have ShareableContent ct
    try:
        sc = ShareableContent.objects.get(shared_content_type=ct)
        logger.debug("Drop ShareableContent for %r" % ct)
        sc.delete()
    except ShareableContent.DoesNotExist:
        pass
    # Confirm NOT in get_shareables
    if get_shareables().has_key(mc.__name__.lower()):
        raise SharingError("%s is not a shared feature but somehow snuck into get_shareables()" % mc.__name__)
            
def sharing_enable(mc):
    """
    Enable sharing for a model
    """
    ct = ContentType.objects.get_for_model(mc)
    logger.debug("Insert can_share Permissions and ShareableContent for %r" % ct)
    # Make sure ShareableContent instance exists
    # TODO FeatureContainers and arrays
    try:
        sc = ShareableContent.objects.get(shared_content_type=ct)
        logger.debug("  ShareableContent already exists for %r - do nothing" % ct)
    except ShareableContent.DoesNotExist:
        logger.debug("  Creating shareableContent for %r" % ct)
        sc = ShareableContent.objects.create(shared_content_type=ct) #container_content_type=array_ct, container_set_property='mpa_set')
        sc.save()
    # Make sure Feature has can_share_* permission;
    codename = "can_share_%s" % mc._meta.module_name
    try:
        p = Permission.objects.get(codename=codename)
        logger.debug("  can_share Permission already exists for %r - do nothing" % mc)
    except Permission.DoesNotExist:
        logger.debug("  Creating permissions for %s and ct # %s (%r)" % (codename, ct.id, ct))
        p = Permission.objects.create(codename=codename,name=codename.replace('_',' '),content_type_id=ct.id)
        p.save()
    # Confirm in get_shareables
    if not get_shareables().has_key(mc.__name__.lower()):
        raise SharingError("%s uses ShareableGeoManager but is not in get_shareables()" % mc.__name__)
