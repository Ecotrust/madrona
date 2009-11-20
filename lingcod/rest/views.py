from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.template import loader

def get_object_for_editing(request, klass, pk):
    """
    Returns 404 if object cannot be found, or 403 if the user is not 
    authorized to modify an object.

    usage:

    instance = get_object_for_editing(Mpa, 12)
    if isinstance(instance, HttpResponse):
        return instance
    ...

    """
    instance = get_object_or_404(klass, pk=pk)
    if not request.user.is_authenticated():
        return HttpResponse('You must be logged in.', status=401)
    # Check that user owns the object or is staff
    if not request.user.is_staff and request.user != instance.user:
        return HttpResponseForbidden('You do not have permission to modify this object.')
    return instance

def get_object_for_viewing(request, klass, pk):
    instance = get_object_or_404(klass, pk=pk)
    if not request.user.is_authenticated:
        return HttpResponse('You must be logged in.', status=401)
    # This isn't implemented properly yet. Should check lingcod.sharing to see
    # if user has permission to view
    # something like:
    # 
    # lingcod.sharing.utils.can_user_view(user, instance)
    # 
    return instance

# RESTful Generic Views

def delete(request, model=None, pk=None):
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
    if request.method == 'DELETE':        
        if model is None or pk is None:
            raise Exception('delete view not configured properly.')
        instance = get_object_for_editing(request, model, pk)
        if isinstance(instance, HttpResponse):
            # get_object_for_editing is trying to return a 404, 401, or 403
            return instance

        instance.delete()
        return HttpResponse('Deleted.')
    else:
        return HttpResponse('DELETE http method must be used to delete', status=405)

def create(request, form_class=None, action=None, title="New"):
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
    if form_class is None or action is None:
        raise Exception('create view not configured properly.')
    if not request.user.is_authenticated():
        return HttpResponse('You must be logged in.', status=401)    
    if request.method == 'POST':
        request.POST['user'] = request.user.pk
        form = form_class(request.POST)
        # form.fields['user'] = request.user.pk
        if form.is_valid():
            m = form.save()
            response = HttpResponse('created', status=201)
            response['Location'] = m.get_absolute_url()
            return response
        else:
            c = RequestContext(request, {
                'form': form,
                'title': title,
                'action': action,
            })
            t = loader.get_template('rest/form.html')
            return HttpResponse(t.render(c), status=400)
    else:
        return HttpResponse('Invalid http method', status=405)

def create_form(request, form_class=None, action=None, extra_context={}, 
    title="New", template='rest/form.html'):
    """
    Serves a form for creating new objects
    
    GET only
    """
    if form_class is None or action is None:
        raise Exception('create_form view is not configured properly.')
    if not request.user.is_authenticated():
        return HttpResponse('You must be logged in.', status=401)
    if request.method == 'GET':
        return render_to_response(template, {
            'form': form_class(),
            'title': title,
            'action': action,
        })
    else:
        return HttpResponse('Invalid http method', status=405)
        

def update(request, form_class=None, pk=None):
    """
        When calling, provide the request object, a model class, and the
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
    if form_class is None or pk is None:
        raise Exception('update view not configured properly.')
    instance = get_object_for_editing(request, form_class.Meta.model, pk)
    if isinstance(instance, HttpResponse):
        # get_object_for_editing is trying to return a 404, 401, or 403
        return instance
    try:
        instance.get_absolute_url()
    except:
        raise Exception('Model to be edited must have get_absolute_url defined.')
    try:
        instance.name
    except:
        raise Exception('Model to be edited must have a name attribute.')
        
    if request.method == 'POST':
        request.POST['user'] = request.user.pk
        form = form_class(request.POST)
        # form.fields['user'] = request.user.pk
        if form.is_valid():
            m = form.save()
            return HttpResponse('updated', status=200)
        else:
            c = RequestContext(request, {
                'form': form,
                'title': instance.name,
                'action': instance.get_absolute_url(),
            })
            t = loader.get_template('rest/form.html')
            return HttpResponse(t.render(c), status=400)
    else:
        return HttpResponse("""Invalid http method. 
        Yes we know, PUT is supposed to be used rather than POST, 
        but it was much easier to implement as POST :)""", status=405)

def update_form(request, form_class=None, pk=None, extra_context={}, 
    template='rest/form.html'):
    """
    Returns a form for editing features
    """
    if form_class is None or pk is None:
        raise Exception('update view not configured properly.')
    instance = get_object_for_editing(request, form_class.Meta.model, pk)
    if isinstance(instance, HttpResponse):
        # get_object_for_editing is trying to return a 404, 401, or 403
        return instance
    try:
        instance.get_absolute_url()
    except:
        raise Exception('Model to be edited must have get_absolute_url defined.')
    try:
        instance.name
    except:
        raise Exception('Model to be edited must have a name attribute.')
        
    if request.method == 'GET':
        form = form_class(instance=instance)
        return render_to_response(template, {
            'form': form,
            'title': instance.name,
            'action': instance.get_absolute_url(),
        })
    else:
        return HttpResponse('Invalid http method', status=405)
        
    
def resource(request, form_class=None, pk=None, get_func=None, 
    extra_context={}, template="rest/show.html"):
    """
    Provides a resource for a django model that can be utilized by the 
    lingcod.rest client module.
    
    Implements actions for the following http actions:
    
        POST:   Update an object
        DELETE: Delete it
        GET:    Provide a page representing the model. For MPAs, this is the 
                MPA attributes screen. The marinemap client will display this
                page in the sidebar whenever the object is brought into focus. 

                To implement GET, this view needs to be passed a view function
                that returns an HttpResponse or a template can be specified
                that will be passed the instance and an optional extra_context
        
    Makes use of lingcod.rest.views.update and lingcod.rest.views.delete
    """
    if form_class is None or pk is None:
        raise Exception('lingcod.rest.views.resource not setup with correct arguments')
    if request.method == 'DELETE':
        return delete(request, form_class.Meta.model, pk)
    elif request.method == 'GET':
        instance = get_object_for_viewing(request, form_class.Meta.model, pk)
        if get_func is not None:
            return get_func(request, instance)
        else:
            return render_to_response(template, {
                'instance': instance,
            })
    elif request.method == 'POST':
        return update(request, form_class, pk)