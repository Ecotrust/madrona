from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti, get_mpa_class
from lingcod.sharing.utils import get_viewable_object_or_respond
from lingcod.manipulators.manipulators import * 
from manipulators import *
from django.contrib.gis.geos import *
from django.core import urlresolvers
from django.conf import settings
#from cjson import encode as json_encode
from django.utils import simplejson

import models

def mlpaManipulators(request, template_name='common/mlpa-manipulators.html'):
    return render_to_response(template_name, RequestContext(request,{'api_key':settings.GOOGLE_API_KEY}))
    
def mpa_remove_spikes(request, mpa_id):
    mpa_id = int(mpa_id)
    mpa_class = get_mpa_class()
    mpa = get_viewable_object_or_respond(mpa_class,mpa_id,request.user)
    mpa.remove_spikes()
    mpa_admin_url = urlresolvers.reverse('admin:mlpa_mlpampa_change',args=(mpa.pk,))
    return HttpResponseRedirect(mpa_admin_url)