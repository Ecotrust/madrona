from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from django.conf import settings
from django.utils import simplejson

import models
from forms import MpaForm, LoadForm

def mpaLoadForm(request, loadform, form_template='mpa/mpa_load_form.html'):
    '''
        Handler for load form request
    '''
    if request.method == 'GET':
        #action = '.'
        opts = {
            'form': loadform,
            #'action': action,
        }
        return render_to_response(form_template, RequestContext(request, opts))
    else:
        return HttpResponse( "MPA Load Form request received unexpected " + request.method + " request.", status=400 )

def mpaLoad(request, mpas, loadform, loaded_template='mpa/mpa_loaded.html', form_template='mpa/mpa_load_form.html', error_template='mpa/mpa_load_error.html'):
    '''
        Handler for load form submission
    '''
    if request.method == 'GET':
        if loadform.is_valid():
            user = loadform.cleaned_data['user']
            name = loadform.cleaned_data['name']
            #if there's more than one, then take the last one 
            #this is temporary until we have other things in place, such as user log in, and arrays
            if len(mpas) > 0:
                mpa = mpas[len(mpas)-1] 
                return buildJsonResponse(mpa, loaded_template)
            else:
                html = render_to_string(error_template, RequestContext(request, {'name': name, 'user': user}))
                return HttpResponse(simplejson.dumps({"html": html, "success": '0'}))
        else:
            action = '/mpa/load/form/'
            opts = {
                'form': loadform,
                'action': action,
            }
            return render_to_response(form_template, RequestContext(request, opts))
    else:
        return HttpResponse( "MPA Load request received unexpected " + request.method + " request.", status=400 )
   
def mpaCommit(request, mpaform, form_template='mpa/mpa_save_form.html', mpa_template='mpa/mpa_saved.html'):
    '''
        Handler for save form request and submission
    '''
    if request.method == 'POST':
        if mpaform.is_valid():
            transformForDB(mpaform.cleaned_data['geometry_orig'])
            transformForDB(mpaform.cleaned_data['geometry_final'])
            mpaform.save()
            opts = {
                'name': mpaform.cleaned_data['name']
            }
            return render_to_response(mpa_template, RequestContext(request, opts))
        else:
            action = '/mpa/'
            opts = {
                'form': mpaform,
                'action': action,
            }
            return render_to_response(form_template, RequestContext(request, opts))
    elif request.method == 'GET':
        action = '/mpa/'
        opts = {
            'form': mpaform,
            'action': action,
        }
        return render_to_response(form_template, RequestContext(request, opts))
    else:
        return HttpResponse( "MPA Commit request received unexpected " + request.method + " request.", status=400 )
     
def buildJsonResponse(mpa, template):
    '''
        Given an mpa (query return from db), and a template (html),
            returns an json response
    '''
    #id = mpa.id
    status_html = render_to_string(template, {'MEDIA_URL':settings.MEDIA_URL, 'name':mpa.name})
    success = '1'
        
    mpa.geometry_orig.transform(settings.GEOMETRY_CLIENT_SRID)
    geojson_orig = mpa.geometry_orig.geojson
    mpa.geometry_final.transform(settings.GEOMETRY_CLIENT_SRID)
    geojson_clipped = mpa.geometry_final.geojson
    
    return HttpResponse(simplejson.dumps({"geojson_orig": geojson_orig, "geojson_clipped": geojson_clipped, "html": status_html, "success": success}))

def extractCoords(geom):
    '''
        Extracts coordinates from a geometry into (long,lat) list 
    '''
    points = [point for point in geom[0]]
    rpoints = [(point[1],point[0]) for point in points]
    return rpoints
    
def transformForDB(geom):
    '''
        Assumes a client side srid
        Transforms given geometry to DB srid 
    '''
    geom.set_srid(settings.GEOMETRY_CLIENT_SRID)
    geom.transform(settings.GEOMETRY_DB_SRID)

def kmlDocWrap( string ):
    '''
        Wraps a given string (should be kml geometry) in Placemark kml
    '''
    return '<Document><Placemark id="coords"> <Style> <LineStyle><color>ffffffff</color><width>2</width></LineStyle> <PolyStyle><color>8000ff00</color></PolyStyle> </Style>'+string+'</Placemark></Document>'


from lingcod.rest.views import delete, update
from lingcod.common.utils import get_mpa_class

def mpa(request, pk):
    """
    Implements lingcod.rest.update, delete, and attributes html view
    """
    if request.method == 'DELETE':
        return delete(request, get_mpa_class(), pk)
    elif request.method == 'GET':
        # return attributes html
        pass
    elif request.method == 'POST':
        update(request, get_mpa_class.Options.form_class, pk)

def copy(request, pk):
    """
    Creates a copy of the given MPA 
    On success, Return status 201 with Location set to new MPA
    Permissions: Need to either own or have shared with you to make copy
    """
    if request.method == 'POST':
        # Authenticate
        user = request.user
        if user.is_anonymous() or not user.is_authenticated():
            return HttpResponse(txt + 'You must be logged in', status=401)

        Mpa = get_mpa_class()
        
        from lingcod.sharing.utils import can_user_view
        viewable, response = can_user_view(Mpa, pk, user) 
        if not viewable:
            return response
        else:
            the_mpa = Mpa.objects.get(pk=pk)

        # Go ahead and make a copy
        new_mpa = the_mpa.copy(user)

        Location = new_mpa.get_absolute_url()
        res = HttpResponse("A copy of MPA %s was made; see %s" % (pk, Location), status=201)
        res['Location'] = Location
        return res
    else:
        return HttpResponse( "MPA copy service received unexpected " + request.method + " request.", status=400 )
