from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from models import *
from lingcod.common import mimetypes

def get_public_layers(request):
    """Returns uploaded kml from the :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` object marked ``active``.
    """
    layer = get_object_or_404(PublicLayerList, active=True)
    return HttpResponse(layer.kml.read(), mimetype=mimetypes.KML)