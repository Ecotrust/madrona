from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render_to_response
from models import *
import os
import itertools
import posixpath
import urllib
import mimetypes as _mimetypes
from django.conf import settings
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common.utils import load_session
from lingcod.sharing.utils import can_user_view
from django.core.urlresolvers import reverse

def get_user_layers(request, session_key='0', input_username=None):
    """Returns uploaded kml from the :class:`UserLayerList <lingcod.layers.models.UserLayerList>`.
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    elif input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)
    
    #ALSO, how to handle a user being associated with more than one active layer?
    layer = get_object_or_404(UserLayerList, user=user.id, active=True)
    return HttpResponse(layer.kml.read(), mimetype=mimetypes.KML)

def get_networklink_private_layers(request, session_key):
    """
    Private layers are shared superoverlays or privatelayers 
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layers = get_layers_for_user(user)
    superoverlays = get_superoverlays_for_user(user)
    response = render_to_response('layers/network_links.kml', 
            {'username': user.username, 'session_key': session_key, 'superoverlays': superoverlays, 'layers': layers}, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=private_links.kml'
    return response

def get_networklink_user_uploaded_layers(request, session_key):
    """ 
    User Uploaded layers are privatelayers
    that are owned by non-staff
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layers = get_layers_for_user(user, allow_owned_by_staff=False)
    response = render_to_response('layers/network_links.kml', 
            {'username': user.username, 'session_key': session_key, 'layers': layers}, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=private_links.kml'
    return response

def get_networklink_protected_layers(request, session_key):
    """ 
    Protected layers are superoverlays or privatelayers
    that are owned by staff
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layers = get_layers_for_user(user,staff_only=True)
    superoverlays = get_superoverlays_for_user(user,staff_only=True)
    response = render_to_response('layers/network_links.kml', 
            {'username': user.username, 'session_key': session_key, 'superoverlays': superoverlays, 'layers': layers}, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=private_links.kml'
    return response

def get_layerlist(request,session_key):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    urls = []

    layers = get_layers_for_user(user)
    print layers
    for layer in layers:
        url = reverse('layers-private', kwargs={'pk': layer.pk, 'session_key': session_key})
        urls.append(url)

    layers = get_superoverlays_for_user(user)
    print layers
    for layer in layers:
        url = reverse('layers-superoverlay-private', kwargs={'pk': layer.pk, 'session_key': session_key})
        urls.append(url)

    # TODO how should these be returned? certainly not a comma-seperated list
    lstr = ','.join(urls)
    return HttpResponse(lstr, status=200)

def get_superoverlays_for_user(user, staff_only=False):
    shared_overlays = PrivateSuperOverlay.objects.shared_with_user(user).order_by('-priority')
    owned_overlays = PrivateSuperOverlay.objects.filter(user=user).order_by('-priority')
    layers = []
    for lyr in itertools.chain(shared_overlays, owned_overlays):
        if lyr not in layers:
            if not staff_only or (staff_only and lyr.user.is_staff):
                layers.append(lyr)
    return layers

def get_layers_for_user(user, allow_owned_by_staff=True, staff_only=False):
    shared_layers = PrivateLayerList.objects.shared_with_user(user).order_by('-priority')
    owned_layers = PrivateLayerList.objects.filter(user=user).order_by('-priority')
    layers = []
    for lyr in itertools.chain(owned_layers, shared_layers):
        if lyr not in layers:
            if allow_owned_by_staff or (not allow_owned_by_staff and not lyr.user.is_staff):
                if not staff_only or (staff_only and lyr.user.is_staff):
                    layers.append(lyr)
    return layers

def get_private_layer(request, pk, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    viewable, response = can_user_view(PrivateLayerList, pk, user)
    if not viewable:
        return response
    else:
        layer = PrivateLayerList.objects.get(pk=pk)
        response = HttpResponse(layer.kml.read(), status=200, mimetype=mimetypes.KML)
        response['Content-Disposition'] = 'attachment; filename=private_%s.kml' % pk
        return response

def get_private_superoverlay(request, pk, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    viewable, response = can_user_view(PrivateSuperOverlay, pk, user)
    print user, viewable, response
    if not viewable:
        return response
    else:
        layer = PrivateSuperOverlay.objects.get(pk=pk)
        response = HttpResponse(open(layer.base_kml,'rb').read(), status=200, mimetype=mimetypes.KML)
        response['Content-Disposition'] = 'attachment; filename=private_overlay_%s.kml' % pk
        return response

def get_relative_to_private_superoverlay(request, pk, path, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    viewable, response = can_user_view(PrivateSuperOverlay, pk, user)
    if not viewable:
        return response

    layer = PrivateSuperOverlay.objects.get(pk=pk)

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


def get_map(request, session_key, input_username, group_name, layer_name, z=None, x=None, y=None, ext=None, root=settings.USER_DATA_ROOT):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    elif input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)

    root_path = os.path.join(root, 'ncc', group_name, layer_name)
    if z is None:
        doc_file = os.path.join(root_path, 'doc.kml')
        doc_kml = open(doc_file).read()
        return HttpResponse(doc_kml, mimetype=mimetypes.KML)  
    elif ext == 'kml':
        kml_file = os.path.join(root_path, z, x, y+'.kml')
        tile_kml = open(kml_file).read()
        return HttpResponse(tile_kml, mimetype=mimetypes.KML)
    else:
        png_file = os.path.join(root_path, z, x, y+'.png')
        tile_png = open(png_file, "rb").read()
        return HttpResponse(tile_png, mimetype='image/png')
    
def get_public_layers(request):
    """Returns uploaded kml from the :class:`PublicLayerList <lingcod.layers.models.PublicLayerList>` object marked ``active``.
    """
    try:
        layer = PublicLayerList.objects.filter(active=True)[0]
    except:
        raise Http404
    response = HttpResponse(layer.kml.read(), mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=public.kml'
    return response
