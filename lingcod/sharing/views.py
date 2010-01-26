# Create your views here.
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from models import get_shareables

def get_shared_content_instance(ctid, pk, user):
    """
     Make sure user owns content and that content is shareable
    """
    ct = ContentType.objects.get(pk=ctid)
    # shareable?
    assert ct.model_class().__name__.lower() in get_shareables()
    obj = ct.model_class().objects.get(pk=pk, user=user)
    return obj
    
def get_sharing_groups(ctid, user):
    """
     Get a list of users groups that have appropriate permissions for this object
    """
    ct = ContentType.objects.get(pk=ctid)
    model_class, permission = get_shareables()[ct.model_class().__name__.lower()]
    groups = user.groups.filter(permissions=permission)
    return groups

def share_form(request, pk, object_type):
    user = request.user

    if request.method == 'GET':
        # Display the form
        # User must be logged in
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse('You must be logged in', status=401)

        # Make sure user owns content and that content is shareable
        obj = get_shared_content_instance(object_type, pk, user)
        obj_type_verbose = obj._meta.verbose_name

        # Get a list of users groups that have appropriate permissions for this object
        groups = get_sharing_groups(object_type, user)

        #return HttpResponse("User %s is sharing object type %s with pk %s <br/> %s" % (user, object_type, pk, groups ) )
        return render_to_response('share_form.html', {'groups': groups, 'obj': obj, 'obj_type_verbose': obj_type_verbose,  'user':user}) 

    elif request.method == 'POST':
        # Must supply a 'share_with' parameter in order to take any action
        try:
            mpa_id = request.REQUEST['mpa_id']
        except:
            return HttpResponse( "Must supply an 'mpa_id' parameter.", status=500 )

        # Check user, group and object permissions

    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )

