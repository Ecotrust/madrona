from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404


def get_object_and_authenticate(request, klass, pk):
    """
    Returns 404 if object cannot be found, or 403 if the user is not 
    authorized to modify an object.

    usage:

    instance = get_object_and_authenticate(Mpa, 12)
    if isinstance(instance, HttpResponse):
        return instance
    ...

    """
    instance = get_object_or_404(klass, pk)
    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in.', status=401)
    # Check that user owns the object or is staff
    if not request.user.is_staff and request.user != instance.user:
        return HttpResponseForbidden('You do not have permission to modify this object.')
    return instance


# RESTful Generic Views

def delete(request, klass, pk):
    """
        When calling, provide the request object, reference to the resource
        class, and the primary key of the object to delete.
    
        Possible response codes:
        
        200: delete operation successful
        401: login required
        403: user does not have permission (not admin user or doesn't own object)
        404: resource for deletion could not be found
        5xx: server error
    """
    instance = get_object_and_authenticate(request, klass, pk)
    if isinstance(instance, HttpResponse):
        # get_object_and_authenticate is trying to return a 404, 401, or 403
        return HttpResponse

    instance.delete()
    HttpResponse('Deleted.')

def create(request, form):
    """
        When calling, provide the request object and a ModelForm class
        
        request types:
            GET:    Provides a form to create a new instance of the model 
                    represented by the ModelForm

                Possible response codes:

                200: OK. Form rendered properly.
                401: Not logged in.
                5xx: Server error.
                
            POST:   Create a new instance from filled out ModelForm

                201: Created. Response body includes representation of resource
                400: Validation error. Response body includes form. Form should
                    be displayed back to the user for correction.
                401: Not logged in.
                5xx: Server error.
    """     
    pass

def update(request, form, pk):
    """
        When calling, provide the request object, a ModelForm class, and the
        primary key of the instance to be updated.
        
        request type:
            GET:    Provides a form for updating the instance.
            
                possible response codes:
                
                200: OK. Form provided in response body.
                401: Not logged in.
                403: Forbidden. User is not staff or does not own object. 
                404: Instance for pk not found.
                5xx: Server error.
                
            POST: Update instance.
            
                possible response codes:
                
                200: OK. Object updated and in response body.
                400: Form validation error. Present form back to user.
                401: Not logged in.
                403: Forbidden. User is not staff or does not own object.
                404: Instance for pk not found.
                5xx: Server error.
    """
    instance = get_object_and_authenticate(request, klass, pk)
    if isinstance(instance, HttpResponse):
        # get_object_and_authenticate is trying to return a 404, 401, or 403
        return HttpResponse        
    pass