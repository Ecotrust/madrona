from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti

from lingcod.manipulators.manipulators import * 
from manipulators import *
from django.contrib.gis.geos import *

from django.conf import settings
#from cjson import encode as json_encode
from django.utils import simplejson

import models

    
def mpaKmlAllGeom(request, id):
    """Handler for AJAX mpaKmlAllGeom request
    """

    mpa = get_object_or_404( models.MlpaMpa, pk=id )
    
    return HttpResponse( KmlWrap( mpa.kmlFolder(request.get_host()) ), content_type='text/plain') 
    
    
def mpaKml(request, id):
    """Handler for AJAX mpaKml request
    """
    mpa = get_object_or_404( models.MlpaMpa, pk=id )
    
    return HttpResponse( KmlWrap( '<Document><name>MPA</name>' + mpa.kmlFinalGeom(request.get_host()) + '</Document>' ), content_type='text/plain')

    
def clipToEstuaries(request):
    '''
        clipToEstuaries currently expects a POST request only
        request should contain two arguments, "target_shape" and "estuaries"
        clipToEstuaries returns an HttpResponse containing the string representation of a json encoded object
        including a status code, a message, and a kml represetation of the estuary clip, the non-estuary clip, and the original geometry
        
        status_code 3 if "target_shape" is not valid geometry
        status_code 2 if no estuaries were found
        status_code 0 if "target_shape" has no estuary overlap
        status_code 4 if "target_shape" is estuary only
        status_code 1 if "target_shape" contains both estuary and oceanic, oceanic part chosen
        status_code 5 if "target_shape" contains both estuary and oceanic, estuary part chosen
        status_code 6 if "target_shape" is not included in POST
    '''
    if request.method != 'POST':
        #return HttpResponse(status=501)
        return HttpResponse( "Manipulator ClipToEstuaries does not support GET requests." )
        
    #if request.method == 'POST':
    target_shape = request.POST.get("target_shape")
    ests = request.POST.get("estuaries")

    #if target_shape is not in the request post return status_code 6
    if target_shape is None:
        return HttpResponse(str(simplejson.dumps({"status_code": '6', "message": 'target_shape was not provided with request', "clipped_shape": None, "original_shape": None})))
    target_shape = fromstr(target_shape)
    
    #THE FOLLOWING WILL NEED TO BE REMOVED when extracting estuaries form database (rather than kwargs)
    if ests is None:
        return HttpResponse(str(simplejson.dumps({"status_code": '6', "message": 'estuaries was not provided with request', "clipped_shape": None, "original_shape": None})))
    estuaries = fromstr(ests)
    
    #clip mpa to estuaries and obtain the larger poly (either estuarine or oceanic)
    estuary_clipper = ClipToEstuariesManipulator(target_shape=target_shape, estuaries=estuaries)
    result = estuary_clipper.manipulate() 
    
    #make sure the geometry was valid 
    if result['status_code'] == '3':
        return HttpResponse(str(simplejson.dumps({"status_code": "3", "message": "New Geometry is NOT valid", "clipped_shape": None, "original_shape": target_shape.kml})))
    #otherwise all returned geometries should have non None values
    return HttpResponse(str(simplejson.dumps({"status_code": result['status_code'], "message": result['message'], "clipped_shape": result['clipped_shape'].kml, "original_shape": result['original_shape'].kml})))

   