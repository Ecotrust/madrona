from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from django.conf import settings
from django.utils import simplejson

import models
from forms import MpaForm, LoadForm

def mpaLoadForm(request, form_template='mpa/mpa_load_form.html'):
    '''
        Handler for load form request
    '''
    if request.method == 'GET':
        loadform = LoadForm()
        #action = '/mpa/'
        opts = {
            'form': loadform,
            #'action': action,
        }
        return render_to_response(form_template, RequestContext(request, opts))

def mpaLoad(request, loaded_template='mpa/mpa_loaded.html', form_template='mpa/mpa_load_form.html', error_template='mpa/mpa_load_error.html'):
    '''
        Handler for load form submission
    '''
    if request.method == 'GET':
        loadform = LoadForm(request.GET)
        if loadform.is_valid():
            user = loadform.cleaned_data['user']
            name = loadform.cleaned_data['name']
            #if there's more than one, then take the last one 
            #this is temporary until we have other things in place, such as user log in, and arrays
            from nc_mlpa.mlpa.models import MlpaMpa
            mpas = MlpaMpa.objects.filter(user=user, name=name)
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
   
def mpaCommit(request, form_template='mpa/mpa_save_form.html', mpa_template='mpa/mpa_saved.html'):
    '''
        Handler for save form request and submission
    '''
    if request.method == 'POST':
        mpaform = MpaForm(request.POST)
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
    if request.method == 'GET':
        mpaform = MpaForm()
        action = '/mpa/'
        opts = {
            'form': mpaform,
            'action': action,
        }
        return render_to_response(form_template, RequestContext(request, opts))
       
def buildJsonResponse(mpa, template):
    '''
        Given an mpa (query return from db), and a template (html),
            returns an json response
    '''
    #id = mpa.id
    clipped_geom, clipped_kml = transformAndWrapForClient(mpa.geometry_final)
    original_geom, original_kml = transformAndWrapForClient(mpa.geometry_orig)
    status_html = render_to_string(template, {'MEDIA_URL':settings.MEDIA_URL, 'name':mpa.name})
    success = '1'
    clipped_wkt = str(clipped_geom) 
    original_coords = extractCoords(original_geom)
    return HttpResponse(simplejson.dumps({"clipped_kml": clipped_kml, "clipped_wkt": clipped_wkt, "original_coords":original_coords, "html": status_html, "success": success}))
    #return HttpResponse(simplejson.dumps({"id": id, "clipped_kml": clipped_kml, "clipped_wkt": clipped_wkt, "original_coords":original_coords, "html": status_html, "success": success}))
 
def extractCoords(geom):
    '''
        Extracts coordinates from a geometry into (long,lat) list 
    '''
    points = [point for point in geom[0]]
    rpoints = [(point[1],point[0]) for point in points]
    return rpoints
     
def transformAndWrapForClient(geom):
    '''
        transforms geometry to client srid 
        returns a wkt version of the geometry, and a kml wrapped version of geometry 
    '''
    new_geom = geom
    new_geom.transform(settings.GEOMETRY_CLIENT_SRID)
    new_kml = kmlDocWrap(new_geom.kml) 
    return new_geom, new_kml
          
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
