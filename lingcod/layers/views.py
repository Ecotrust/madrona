from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404, render_to_response
from models import *
import os
import itertools
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
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layers = get_layers_for_user(user)
    response = render_to_response('layers/network_links.kml', 
            {'username': user.username, 'session_key': session_key, 'layers': layers}, mimetype=mimetypes.KML)
    response['Content-Disposition'] = 'attachment; filename=private_links.kml'
    print response.content
    return response

def get_layerlist(request,session_key):
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    layers = get_layers_for_user(user)
    urls = []
    for layer in layers:
        url = reverse('layers-private', kwargs={'pk': layer.pk, 'session_key': session_key})
        urls.append(url)
    # TODO how should these be returned? certainly not a comma-seperated list
    lstr = ','.join(urls)
    return HttpResponse(lstr, status=200)

def get_layers_for_user(user):
    shared_layers = PrivateLayerList.objects.shared_with_user(user).order_by('-priority')
    owned_layers = PrivateLayerList.objects.filter(user=user).order_by('-priority')
    layers = []
    for lyr in itertools.chain(owned_layers, shared_layers):
        if lyr not in layers:
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
