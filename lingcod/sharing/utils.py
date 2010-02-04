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
    except model_class.DoesNotExist:
        try: 
            # ... finally see if its shared with the user
            obj = model_class.objects.shared_with_user(user).get(pk=pk)
        except model_class.DoesNotExist:
            return HttpResponse("Access denied", status=403)

    return obj

