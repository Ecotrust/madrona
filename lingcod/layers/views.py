from django.http import HttpResponse, Http404
#, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from models import *
import os
import itertools
import posixpath
import urllib
import mimetypes as _mimetypes
from django.conf import settings
from django.template.loader import get_template
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common.utils import load_session
from django.core.urlresolvers import reverse
from lingcod.features.views import get_object_for_viewing
from django.contrib.auth.models import Group
from lingcod.common.utils import is_text

def get_kml_file(request, uid, session_key='0', input_username=None):
    load_session(request, session_key)
    user = request.user

    if input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)
    
    instance = get_object_for_viewing(request, uid)
    if isinstance(instance, HttpResponse):
        return instance

    full = instance.kml_full
    response = HttpResponse(full)
    if is_text(full):
        response['Content-Type'] = mimetypes.KML
    else:
        response['Content-Type'] = mimetypes.KMZ
    return response

def is_privatekml_viewable(layer, user):
    """
    Since privatekmls are not Features, they get their own sharing scheme
    """
    if user.is_anonymous() or not user.is_authenticated():
        return False, HttpResponse('You must be logged in', status=401)

    for user_group in user.groups.all():
        if user_group in layer.sharing_groups.all():
            return True, HttpResponse('User %s has permission to view %s' % (user.username, layer.name))

    return False, HttpResponse('Access denied', status=403)

def get_privatekml_list(request, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    all_kmls = PrivateKml.objects.all()
    accessible_kmls = []
    for kml in all_kmls:
        viewable, response = is_privatekml_viewable(kml, user)
        if viewable:
            accessible_kmls.append(kml)

    t = get_template('layers/private.kml')
    kml = t.render(RequestContext( request, {'session_key': session_key, 
                                             'kmls': accessible_kmls}))
    response = HttpResponse(kml, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'filename=privatekml_%s.kml' % user.username
    return response

def has_privatekml(user):
    """
    Returns a boolean - does user have any private kmls shared with them?
    """
    all_kmls = PrivateKml.objects.all()
    accessible_kmls = []
    for kml in all_kmls:
        viewable, response = is_privatekml_viewable(kml, user)
        if viewable:
            accessible_kmls.append(kml)
    if len(accessible_kmls) >= 1:
        return True
    else:
        return False

def get_privatekml(request, pk, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layer = PrivateKml.objects.get(pk=pk)
    viewable, response = is_privatekml_viewable(layer, user)
    if not viewable:
        return response
    else:
        mimetype, encoding = _mimetypes.guess_type(layer.base_kml)
        mimetype = mimetype or 'application/octet-stream'
        response = HttpResponse(open(layer.base_kml,'rb').read(), status=200, mimetype=mimetype)
        response['Content-Disposition'] = 'filename=privatekml_%s.kml' % pk
        return response

def get_relative_to_privatekml(request, pk, path, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layer = PrivateKml.objects.get(pk=pk)
    viewable, response = is_privatekml_viewable(layer, user)
    if not viewable:
        return response

    # From django.views.static
    path = posixpath.normpath(urllib.unquote(path))
    path = path.lstrip('/')
    newpath = ''
    for part in path.split('/'):
        if not part:
            # Strip empty path components.
            continue
        drive, part = os.path.splitdrive(part)
        head, part = os.path.split(part)
        if part in (os.curdir, os.pardir):
            # Strip '.' and '..' in path.
            continue
        newpath = os.path.join(newpath, part).replace('\\', '/')

    # newpath is different from path any time path is unsafe. 
    if newpath and path == newpath:
        basedir = os.path.dirname(layer.base_kml)
        requested_file = os.path.join(basedir,newpath)
        if not os.path.exists(requested_file):
            raise Http404
        mimetype, encoding = _mimetypes.guess_type(requested_file)
        mimetype = mimetype or 'application/octet-stream'
        return HttpResponse(open(requested_file,'rb').read(), status=200, mimetype=mimetype)
    else:
        return HttpResponse("Nice try", status=403)

def get_public_layers(request):
    """Returns uploaded kml from the :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` 
    object marked ``active``.
    """
    try:
        layer = PublicLayerList.objects.filter(active=True)[0]
    except:
        raise Http404
    response = HttpResponse(layer.kml_file.read(), mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=public.kml'
    return response

