# Create your views here.
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.contrib.contenttypes.models import ContentType
from models import get_shareables, share_object_with_groups

def get_shared_content_instance(ctid, pk, user):
    """
     Make sure user owns content and that content is shareable
    """
    try:
        ct = ContentType.objects.get(pk=ctid)
        # shareable?
        assert ct.model_class().__name__.lower() in get_shareables()
        obj = ct.model_class().objects.get(pk=pk, user=user)
        return obj
    except:
        return None
    
def get_sharing_groups(ctid, user):
    """
     Get a list of users groups that have appropriate permissions for this object
    """
    try:
        ct = ContentType.objects.get(pk=ctid)
        model_class, permission = get_shareables()[ct.model_class().__name__.lower()]
        groups = user.groups.filter(permissions=permission)
        return groups
    except:
        return None

def share_form(request, pk, object_type):
    # User must be logged in
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)

    # Make sure user owns content and that content is shareable
    obj = get_shared_content_instance(object_type, pk, user)
    if not obj:
        return HttpResponse("This object is not shareable.", status=404)
    obj_type_verbose = obj._meta.verbose_name

    if request.method == 'GET':
        # Display the form
        # Which groups is this object already shared to?
        already_shared_groups = obj.sharing_groups.all()

        # Get a list of users groups that have appropriate permissions for this object
        groups = get_sharing_groups(object_type, user)
        if not groups:
            return HttpResponse("There are no groups to which you can share your content at this time.", status=404)

        return render_to_response('share_form.html', {'groups': groups, 'already_shared_groups': already_shared_groups, 'obj': obj, 
                                                      'obj_type_verbose': obj_type_verbose,  'user':user}) 

    elif request.method == 'POST':
        group_ids = [int(x) for x in request.POST.getlist('sharing_groups')]

        try:
            share_object_with_groups(obj,group_ids)
            if len(group_ids) == 0:
                restext = "<br/><p id='sharing_response'>The %s named %s is now unshared with all groups.</p id='sharing_response'>" % (obj_type_verbose, unicode(obj))
            else:
                restext = "<br/><p id='sharing_response'>The %s named %s is now shared with groups %s</p id='sharing_response'>" % (obj_type_verbose, unicode(obj), ','.join([str(x) for x in group_ids]))
            return HttpResponse(restext,status=200)
        except:
            return HttpResponse('Unable to share objects with those specified groups', status=500)

    else:
        return HttpResponse( "Array-MPA service received unexpected " + request.method + " request.", status=400 )

