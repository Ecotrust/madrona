from django.shortcuts import render_to_response
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from lingcod.common import mimetypes
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
from django.http import Http404
from lingcod.common.utils import load_session
from lingcod.sharing.models import get_content_type_id

def get_user_mpa_data(user):
    """
    Organizes user's MPAs into arrays and provides their designations.
    Just basically a data structure manipulation on the queryset.

    The template expects something like:
     {'array name + id': {'array': array_object, 'mpas': [mpa1, mpa2] } }
    """
    Mpa = utils.get_mpa_class()

    mpas = Mpa.objects.filter(user=user).add_kml()

    unattached = utils.get_array_class()(name='Marine Protected Areas')
    shapes = {'Unattached': {'array': unattached, 'mpas':[]} }
    for mpa in mpas:
        if not mpa.array:
            shapes['Unattached']['mpas'].append(mpa)
        else:
            array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
            if array_nameid in shapes.keys():
                shapes[array_nameid]['mpas'].append(mpa)
            else:
                shapes[array_nameid] = {'array': mpa.array, 'mpas':[mpa]}
    for array in utils.get_array_class().objects.empty().filter(user=user):
        array_nameid = "%s_%d" % (array.name, array.id)
        shapes[array_nameid] = {'array': array, 'mpas':[]}
    designations = MpaDesignation.objects.all()
    return shapes, designations

def get_array_mpa_data(user, input_array_id):
    """
    Organizes MPAs belonging to a given array and provides their designations.
    Just basically a data structure manipulation on the queryset.
    """
    Mpa = utils.get_mpa_class()
    MpaArray = utils.get_array_class()

    try:
        the_array = MpaArray.objects.get(id=input_array_id, user=user)
    except:
        raise Http404
    mpas = the_array.mpa_set.add_kml()
    array_nameid = "%s_%d" % (the_array.name, the_array.id)
    shapes = {array_nameid: {'array':the_array, 'mpas': []} }
    for mpa in mpas:
        if array_nameid in shapes.keys():
            shapes[array_nameid]['mpas'].append(mpa)
        else:
            raise Http404
    designations = MpaDesignation.objects.all()
    return shapes, designations

def get_single_mpa_data(user, input_mpa_id):
    """
    Creates data structure for a single MPA and its designation.
    Just basically a data structure manipulation on the queryset.
    """
    Mpa = utils.get_mpa_class()

    try:
        mpas = Mpa.objects.filter(id=input_mpa_id, user=user).add_kml()
        mpa = mpas[0]
    except:
        raise Http404

    if mpa.array:
        array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
        shapes = {array_nameid: {'array':mpa.array, 'mpas': [mpa]} }
    else:
        unattached = utils.get_array_class()(name='Unattached')
        shapes = {'Unattached': {'array': unattached, 'mpas':[mpa]} }
    designations = [mpa.designation]
    return shapes, designations

def get_mpas_shared_by(shareuser, sharegroup, user):
    """
    Creates data structure for a single MPA and its designation.
    Just basically a data structure manipulation on the queryset.
    """
    Mpa = utils.get_mpa_class()
    sg = Group.objects.get(pk=sharegroup)
    su = User.objects.get(pk=shareuser)

    # TODO: sharing 
    try:
        mpas = Mpa.objects.shared_with_user(user).filter(sharing_groups=sg, user=su).add_kml()
    except:
        raise Http404

    unattached = utils.get_array_class()(name='Marine Protected Areas')
    shapes = {'Unattached': {'array': unattached, 'mpas':[]} }
    for mpa in mpas:
        if not mpa.array:
            shapes['Unattached']['mpas'].append(mpa)
        else:
            array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
            if array_nameid in shapes.keys():
                shapes[array_nameid]['mpas'].append(mpa)
            else:
                shapes[array_nameid] = {'array': mpa.array, 'mpas':[mpa]}
    designations = MpaDesignation.objects.all()
    return shapes, designations

def create_kmz(kml, zippath):
    """
    Given a KML string and a "/" seperated path like "FOLDERNAME/doc.kml",
    creates a zipped KMZ archive buffer that can be written directly to a 
    django response object
    """
    import tempfile
    from cStringIO import StringIO
    import zipfile

    # write out the kml to tempfile
    kmlfile = tempfile.NamedTemporaryFile()
    kmlfile.write(kml.encode('utf-8'))
    kmlfile.flush()

    # zip it up into a kmz
    kmzbuffer = StringIO()
    zipout = zipfile.ZipFile(kmzbuffer,'w',zipfile.ZIP_DEFLATED)
    zipout.write(kmlfile.name, zippath.encode('ascii')) 
    zipout.close()

    # close out the tempfile
    kmlfile.close()
    # grab the content of the stringIO buffer
    kmz = kmzbuffer.getvalue()
    # close out the stringIO buffer
    kmzbuffer.close()

    return kmz

from django.views.decorators.cache import cache_control

@cache_control(no_cache=True)
def create_kml(request, input_username=None, input_array_id=None, input_mpa_id=None, input_shareuser=None, input_sharegroup=None, links=False, kmz=False, session_key='0'):
    """
    Returns a KML/KMZ containing MPAs (organized into folders by array)
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    elif input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)

    if input_username:
        shapes, designations = get_user_mpa_data(user)
    elif input_array_id:
        shapes, designations = get_array_mpa_data(user, input_array_id)
    elif input_mpa_id:
        shapes, designations = get_single_mpa_data(user, input_mpa_id)
    elif input_shareuser and input_sharegroup:
        shapes, designations = get_mpas_shared_by(input_shareuser, input_sharegroup, user)
    else:
        raise Http404

    # determine content types for sharing
    mpa_ctid = get_content_type_id(utils.get_mpa_class()) 
    array_ctid = get_content_type_id(utils.get_array_class())

    t = get_template('placemarks.kml')
    kml = t.render(Context({'shapes': shapes, 'designations': designations, 'use_network_links': links, 'request_path': request.path, 
                            'session_key': session_key, 'mpa_ctid': mpa_ctid, 'array_ctid': array_ctid}))

    response = HttpResponse()
    response['Content-Disposition'] = 'attachment'
    if kmz:
        kmz = create_kmz(kml, 'mpa/doc.kml')
        response['Content-Type'] = mimetypes.KMZ
        response.write(kmz)
    else:
        response['Content-Type'] = mimetypes.KML
        response.write(kml)
        
    return response

@cache_control(no_cache=True)
def create_shared_kml(request, input_username, kmz=False, session_key='0'):
    """
    Returns a KML/KMZ containing shared MPAs (organized into folders by groups and users who have shared them)
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)
    elif input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)
    
    from lingcod.sharing.models import groups_users_sharing_with 
    sharing_with = groups_users_sharing_with(user)

    t = get_template('shared.kml')
    kml = t.render(Context({'groups_users': sharing_with, 'request_path': request.path, 'session_key': session_key }))

    response = HttpResponse()
    response['Content-Disposition'] = 'attachment'
    if kmz:
        kmz = create_kmz(kml, 'mpa/doc.kml')
        response['Content-Type'] = mimetypes.KMZ
        response.write(kmz)
    else:
        response['Content-Type'] = mimetypes.KML
        response.write(kml)
        
    return response

def public_shared(request):
    return render_to_response('public.kml', {})
