from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

from django.conf import settings

from lingcod.studyregion import models


def regionKml(request):
    """Handler for AJAX regionKml request
    """
    region = get_object_or_404( models.StudyRegion, pk=1 )
    
    return HttpResponse(region.kml(), content_type='text/plain') 
    
        
def regionKmlChunk(request, n, s, e, w):
    """Handler for AJAX regionKml request
    """
    region = get_object_or_404( models.StudyRegion, pk=1 )
    
    return HttpResponse( 
        region.kml_chunk(float(n), float(s), float(e), float(w)), content_type='text/plain') 
            
    
def regionLookAtKml(request):
    """Handler for AJAX regionLookAtKml request
    """
    region = get_object_or_404( models.StudyRegion, pk=1 )
    return HttpResponse( region.lookAtKml(), content_type='text/plain' )