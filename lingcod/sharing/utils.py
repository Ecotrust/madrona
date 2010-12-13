from django.http import HttpResponse, Http404
from models import *

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

