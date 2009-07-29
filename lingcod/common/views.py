from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.studyregion import models
from django.conf import settings


def map(request):
    """Main application window
    """
    return render_to_response('common/map.html', RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))
    
    
def regionKml(request):
    """Handler for AJAX regionKml request
    """
    region = get_object_or_404( models.StudyRegion, pk=1 )
    return HttpResponse( region.kml() )
    
    
def regionLookAtKml(request):
    """Handler for AJAX regionLookAtKml request
    """
    region = get_object_or_404( models.StudyRegion, pk=1 )
    return HttpResponse( region.lookAtKml() )
    