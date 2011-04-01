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
from django.core.urlresolvers import reverse
from lingcod.features.views import get_object_for_viewing
from django.contrib.models import Group

def get_kml_file(request, uid, session_key='0', input_username=None):
    load_session(request, session_key)
    user = request.user

    if input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)
    
    instance = get_object_for_viewing(request, uid)
    if isinstance(instance, HttpResponse):
        return instance

    response = HttpResponse(instance.kml_full)
    response['Content-Type'] = mimetypes.KML
    return response

def is_superoverlay_viewable(layer, user):
    """
    Since superoverlays are not Features, they get their own sharing scheme
    For now, this is a setting; a dict with superoverlay name and list of groups:

    SUPEROVERLAY_GROUPS = {'my_super_overlay': ['RSG Members','My Office Mates']}
    """
    if user.is_anonymous() or not user.is_authenticated():
        return False, HttpResponse('You must be logged in', status=401)

    try:
        perms = settings.SUPEROVERLAY_GROUPS
    except AttributeError:
        return False, HttpResponse('No SUPEROVERLAY_GROUPS defined in settings', status=500)

    overlay_groups = [Group.objects.get(name=x) for x in perms[layername]]
    for user_group in user.groups.all():
        if user_group in overlay_groups:
            return True, HttpResponse('User %s has permission to view %s' % (user.username, layer.name))

    return False, HttpResponse('Access denied', status=403)

def get_private_superoverlay(request, pk, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layer = PrivateLayerList.objects.get(pk=pk)
    viewable, response = is_superoverlay_viewable(layer, user)
    if not viewable:
        return response
    else:
        response = HttpResponse(open(layer.base_kml,'rb').read(), status=200, mimetype=mimetypes.KML)
        response['Content-Disposition'] = 'attachment; filename=superoverlay_%s.kml' % pk
        return response

def get_relative_to_private_superoverlay(request, pk, path, session_key='0'):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layer = PrivateLayerList.objects.get(pk=pk)
    viewable, response = is_superoverlay_viewable(layer, user)
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
    response = HttpResponse(layer.kml_file.read(), mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=public.kml'
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
    superoverlays = get_superoverlays_for_user(user,staff_only=True)
    response = render_to_response('layers/network_links.kml', 
            {'username': user.username, 'session_key': session_key, 'superoverlays': superoverlays}, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=private_links.kml'
    return response

def get_superoverlays_for_user(user, staff_only=False):
    shared_overlays = PrivateSuperOverlay.objects.shared_with_user(user).order_by('-priority')
    owned_overlays = PrivateSuperOverlay.objects.filter(user=user).order_by('-priority')
    layers = []
    for lyr in itertools.chain(shared_overlays, owned_overlays):
        if lyr not in layers:
            if not staff_only or (staff_only and lyr.user.is_staff):
                layers.append(lyr)
    return layers
