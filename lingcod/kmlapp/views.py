from django.shortcuts import render_to_response
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
from django.http import Http404
from lingcod.common.utils import load_session
from lingcod.sharing.models import get_content_type_id
from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.conf import settings

# This is the dict key used for mpas without an array
# Since it's sorted alphabetically by key, this string
# determines where the 'Unattached' MPA folder will appear
UNATTACHED = "zzzzzzz"
# This is the nice name as it will appear on screen
try:
    UNATTACHED_NAME = settings.KML_UNATTACHED_NAME
except:
    UNATTACHED_NAME = "Marine Protected Areas"

def get_user_mpa_data(user):
    """
    Organizes user's MPAs into arrays and provides their designations.
    Just basically a data structure manipulation on the queryset.
    
    Only returns objects owned by user, not shared

    The template expects something like:
     {'array name + id': {'array': array_object, 'mpas': [mpa1, mpa2] } }
    """
    Mpa = utils.get_mpa_class()

    mpas = Mpa.objects.filter(user=user).add_kml()

    unattached = utils.get_array_class()(name=UNATTACHED_NAME)
    shapes = {UNATTACHED: {'array': unattached, 'mpas':[]} }
    for mpa in mpas:
        if not mpa.array:
            shapes[UNATTACHED]['mpas'].append(mpa)
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

def get_public_arrays():
    """
    Organizes MPAs belonging to a public arrays
    No login necessary, everyone sees these
    Public groups defined in settings.SHARING_TO_PUBLIC_GROUPS
    """
    from django.conf import settings
    MpaArray = utils.get_array_class()
    public_groups = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
    public_arrays = MpaArray.objects.filter(sharing_groups__in=public_groups)
    shapes = {}
    for pa in public_arrays:
        array_nameid = "%s_%d" % (pa.name, pa.id)
        shapes[array_nameid] = {'array': pa, 'mpas':pa.mpa_set.add_kml()}
    designations = MpaDesignation.objects.all()
    return shapes, designations
        

def get_array_mpa_data(user, input_array_id):
    """
    Organizes MPAs belonging to a given array and provides their designations.
    Just basically a data structure manipulation on the queryset.
    Will return if user owns the array OR if array is shared with user
    """
    Mpa = utils.get_mpa_class()
    MpaArray = utils.get_array_class()

    try:
        # Frst see if user owns it
        if user.is_anonymous() or not user.is_authenticated():
            raise MpaArray.DoesNotExist
        else:
            the_array = MpaArray.objects.get(id=input_array_id, user=user)
    except MpaArray.DoesNotExist:
        try: 
            # ... then see if its shared with the user
            the_array = MpaArray.objects.shared_with_user(user).get(id=input_array_id)
        except MpaArray.DoesNotExist:
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
    Will return if user owns the mpa OR if mpa is shared with user
    """
    Mpa = utils.get_mpa_class()

    try:
        # Frst see if user owns it
        mpas = list(Mpa.objects.filter(id=input_mpa_id, user=user).add_kml())
        if len(mpas)==0:
            raise Mpa.DoesNotExist
        else:
            mpa = mpas[0]
    except Mpa.DoesNotExist:
        try: 
            # ... then see if its shared with the user
            mpas = list(Mpa.objects.shared_with_user(user).filter(id=input_mpa_id).add_kml())
            if len(mpas)==0:
                raise Mpa.DoesNotExist
            else:
                mpa = mpas[0]
        except Mpa.DoesNotExist:
            raise Http404

    if mpa.array:
        array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
        shapes = {array_nameid: {'array':mpa.array, 'mpas': [mpa]} }
    else:
        unattached = utils.get_array_class()(name=UNATTACHED)
        shapes = {UNATTACHED: {'array': unattached, 'mpas':[mpa]} }
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

    try: 
        # The "right" way but array is a generic FK so this doesn't work
        #mpas = Mpa.objects.shared_with_user(user).filter(
        #        models.Q(sharing_groups=sg) |
        #        models.Q(array__sharing_groups=sg)
        #        )
        mpas = Mpa.objects.shared_with_user(user,filter_groups=[sg]).filter(user=su).add_kml()
    except Mpa.DoesNotExist:
        raise Http404

    unattached = utils.get_array_class()(name=UNATTACHED_NAME)
    shapes = {UNATTACHED: {'array': unattached, 'mpas':[]} }
    for mpa in mpas:
        # Does it belong to an array that is shared?
        if mpa.array and sg in mpa.array.sharing_groups.all():
            array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
            if array_nameid in shapes.keys():
                shapes[array_nameid]['mpas'].append(mpa)
            else:
                shapes[array_nameid] = {'array': mpa.array, 'mpas':[mpa]}
        # Or is it a lone MPA?
        else:
            shapes[UNATTACHED]['mpas'].append(mpa)
    if len(shapes[UNATTACHED]['mpas']) == 0:
        del shapes[UNATTACHED]
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
    #The Problem:  for Windows, we need to close the file before we can access it again below (via zipout.write)
    #   this caused a Permissions Error when running from the local dev server (on Windows)
    #   as Windows considered the unclosed file to already be in use (and therefore unaccessible) 
    #The Solution: adding 'delete=False' to tempfile.NamedTemporaryFiles for developing environments using Python 2.6(sf 2-16-10)
    #   this will only happen if the user is using Python 2.6, previous versions of Python will treat the code as it was
    #   (this delete parameter isn't available until python 2.6)
    #if the development environment is using 2.5 or earlier, then the temp file will still be closed via kmlfile.close()
    #if the development environment is using 2.6 then the temporary file is deleted manually via os.unlink(kmlfile.name) (see below)
    #This was reported (and perhaps more fully explained) in Issue 263
    python26 = True
    try:
        kmlfile = tempfile.NamedTemporaryFile(delete=False)
    except:
        kmlfile = tempfile.NamedTemporaryFile()
        python26 = False
    kmlfile.write(kml.encode('utf-8'))
    kmlfile.flush()
    if python26:
        kmlfile.close() 
    
    # zip it up into a kmz
    kmzbuffer = StringIO()
    zipout = zipfile.ZipFile(kmzbuffer,'w',zipfile.ZIP_DEFLATED)
    zipout.write(kmlfile.name, zippath.encode('ascii')) 
    zipout.close()

    # close out the tempfile
    if python26:
        import os 
        os.unlink(kmlfile.name) 
    else:
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
    if input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)

    organize_in_array_folders = True
    if input_username:
        shapes, designations = get_user_mpa_data(user)
    elif input_array_id:
        shapes, designations = get_array_mpa_data(user, input_array_id)
        organize_in_array_folders = False
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
    kml = t.render(Context({'user': user, 'shapes': sorted(shapes.items()), 'designations': designations, 'use_network_links': links, 'request_path': request.path, 
        'session_key': session_key, 'mpa_ctid': mpa_ctid, 'array_ctid': array_ctid, 'use_array_folders': organize_in_array_folders}))

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
    if input_username and user.username != input_username:
        return HttpResponse('Access denied', status=401)
    
    from lingcod.sharing.models import groups_users_sharing_with 
    sharing_with = groups_users_sharing_with(user)

    t = get_template('shared.kml')
    kml = t.render(Context({'user': request.user, 'groups_users': sharing_with, 'request_path': request.path, 'session_key': session_key}))

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

def shared_public(request, kmz=False, session_key='0'):
    """ 
    Shows all publically shared arrays
    Must be shared with a special set of public groups
    defined in settings.SHARING_TO_PUBLIC_GROUPS
    """
    load_session(request, session_key)
    user = request.user
    shapes, designations = get_public_arrays()

    # determine content types for sharing
    mpa_ctid = get_content_type_id(utils.get_mpa_class()) 
    array_ctid = get_content_type_id(utils.get_array_class())

    t = get_template('placemarks.kml')
    kml = t.render(Context({'loggedin_user': request.user, 'user': request.user, 'shapes': sorted(shapes.items()), 'designations': designations, 'use_network_links': True, 'request_path': request.path, 
        'session_key': session_key, 'mpa_ctid': mpa_ctid, 'array_ctid': array_ctid, 'use_array_folders': False}))

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
