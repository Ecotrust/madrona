from django.template import RequestContext
from django.shortcuts import render_to_response

from django.conf import settings


def snapshot_gadget(request):
    """Gadget xml for sharing map state
    """
    return render_to_response('wave/snapshot.xml', RequestContext(request,{'MEDIA_URL': settings.MEDIA_URL}))

