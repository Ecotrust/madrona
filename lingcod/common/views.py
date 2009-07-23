from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

def map(request, api_key):
    """Main application window
    """
    return render_to_response('common/map.html', RequestContext(request,{'api_key':api_key}))
    