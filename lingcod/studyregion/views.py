from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap

from django.conf import settings

from lingcod.studyregion import models


def studyregion(request, template_name='studyregion/studyregion.html'):
    """Main application window
    """
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))

    
def regionKml(request):
    """Handler for AJAX regionKml request
    """
    region = models.StudyRegion.objects.current()
    
    return HttpResponse( KmlWrap( region.kml(request.get_host()) ), content_type=mimetypes.KML) 
    
        
def regionKmlChunk(request, n, s, e, w):
    """Handler for AJAX regionKml request
    """
    region = models.StudyRegion.objects.current()
    
    return HttpResponse( 
        KmlWrap( '<Document>' + region.kml_chunk(float(n), float(s), float(e), float(w)) + '</Document>' ), content_type=mimetypes.KML) 
            
    
def regionLookAtKml(request):
    """Handler for AJAX regionLookAtKml request
    """
    region = models.StudyRegion.objects.current()
    
    return HttpResponse( KmlWrap( '<Document>' + region.lookAtKml() + '</Document>' ), content_type=mimetypes.KML )