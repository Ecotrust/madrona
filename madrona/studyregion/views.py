from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from madrona.common import default_mimetypes as mimetypes
from madrona.common.utils import KmlWrap
from django.urls import reverse

from django.conf import settings

from madrona.studyregion import models
from django.views.decorators.cache import cache_page

def studyregion(request, template_name='studyregion/studyregion.html'):
    """Main application window
    """
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))

def show(request, pk):
    """Display a map with the study region geometry.
    """
    return render_to_response('studyregion/show.html', RequestContext(request,{'api_key':settings.GOOGLE_API_KEY, 'pk': pk}))

def kml(request, pk):
    """Return kml for the requested StudyRegion
    """
    region = get_object_or_404(models.StudyRegion, pk=pk)
    return HttpResponse(KmlWrap(region.kml(request.get_host())), content_type=mimetypes.KML)

@cache_page(60 * 60 * 24)
def regionKml(request):
    """Handler for AJAX regionKml request
    """
    region = models.StudyRegion.objects.current()

    return HttpResponse(KmlWrap(region.kml(request.get_host())), content_type=mimetypes.KML)


def regionKmlChunk(request, n, s, e, w):
    """Handler for AJAX regionKml request
    """
    region = models.StudyRegion.objects.current()

    return HttpResponse(
        KmlWrap('<Document>' + region.kml_chunk(float(n), float(s), float(e), float(w)) + '</Document>'), content_type=mimetypes.KML)


def regionLookAtKml(request):
    """Handler for AJAX regionLookAtKml request
    """
    region = models.StudyRegion.objects.current()

    return HttpResponse(KmlWrap('<Document>' + region.lookAtKml() + '</Document>'), content_type=mimetypes.KML)
