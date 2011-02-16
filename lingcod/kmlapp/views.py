from django.shortcuts import render_to_response
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common import utils 
from django.http import Http404
from lingcod.common.utils import load_session, get_logger
from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from lingcod.features import get_feature_models, get_collection_models, get_feature_by_uid
from lingcod.features.models import FeatureCollection, Feature
try:
    set
except NameError:
    from sets import Set as set

log = get_logger()

# This is the dict key used for mpas without an array
# Since it's sorted alphabetically by key, this string
# determines where the 'Unattached' MPA folder will appear
UNATTACHED = "zzzzzzz"
# This is the nice name as it will appear on screen
try:
    UNATTACHED_NAME = settings.KML_UNATTACHED_NAME
except:
    UNATTACHED_NAME = "Marine Protected Areas"

def get_styles(features, collections):
    models = []
    models.extend([f.kml_style for f in features])
    models.extend([c.kml_style for c in collections])
    unique_set = set(models)
    return list(unique_set)

def get_user_data(user):
    """
    Organizes user's Features and FeatureCollections.
    Only returns objects owned by user, not shared
    Returns only the features/collections at the top level,
    nested child features will be handled later through
    recursive calls to feature_set.
    """
    toplevel_features = []
    toplevel_collections = []

    # is there a reason to do features vs collections seperately?
    # Perhaps if we need to treat collections differently wrt network links
    for fmodel in get_feature_models():
        #This would be preferable but doesnt really work??
        # unattached = fmodel.objects.filter(collection=None)
        unattached = [x for x in fmodel.objects.filter(user=user) if x.collection is None]
        toplevel_features.extend(unattached)
        
    for cmodel in get_collection_models():
        collections_top = [x for x in cmodel.objects.filter(user=user) if x.collection is None]
        toplevel_collections.extend(collections_top)

    return toplevel_features, toplevel_collections

def get_data_for_feature(user, uid):
    try:
        f = get_feature_by_uid(uid)
    except:
        return False , HttpResponse("Feature %s does not exist" % uid, status=404)

    viewable, response = f.is_viewable(user)
    if not viewable:
        return viewable, response

    features = []
    collections = []

    if isinstance(f, FeatureCollection):
        for fmodel in get_feature_models():
            unattached = [x for x in fmodel.objects.all() if x.collection == f]
            features.extend(unattached)
            
        for cmodel in get_collection_models():
            collections_top = [x for x in cmodel.objects.all() if x.collection == f]
            collections.extend(collections_top)
    elif isinstance(f, Feature):
        features.append(f)

    return features, collections

def get_public_data():
    """
    No login necessary, everyone sees these
    Public groups defined in settings.SHARING_TO_PUBLIC_GROUPS
    """
    from django.conf import settings
    public_groups = Group.objects.filter(name__in=settings.SHARING_TO_PUBLIC_GROUPS)
    features = []
    collections = []

    # Why not user feature_set here? TODO
    for fmodel in get_feature_models():
        #This would be preferable but doesnt really work??
        # unattached = fmodel.objects.filter(collection=None)
        unattached = [x for x in fmodel.objects.filter(sharing_groups__in=public_groups)]
        features.extend(unattached)
        
    for cmodel in get_collection_models():
        collections_top = [x for x in cmodel.objects.filter(sharing_groups__in=public_groups)]
        collections.extend(collections_top)

    return features, collections
        
def get_shared_data(shareuser, sharegroup, user):
    sg = Group.objects.get(pk=sharegroup)
    su = User.objects.get(pk=shareuser)

    features = []
    collections = []

    for fmodel in get_feature_models():
        unattached = [x for x in fmodel.objects.shared_with_user(user, filter_groups=[sg]).filter(user=su) if x.collection is None]
        features.extend(unattached)
        
    for cmodel in get_collection_models():
        collections_top = [x for x in cmodel.objects.shared_with_user(user, filter_groups=[sg]).filter(user=su) if x.collection is None]
        collections.extend(collections_top)

    return features, collections

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

#TODO @cache_control(no_cache=True)
def create_kml(request, input_username=None, input_uid=None, 
        input_shareuser=None, input_sharegroup=None, links=False, kmz=False,
        session_key='0'):
    """
    Returns a KML/KMZ containing Feautures/FeatureCollections owned by user
    """
    load_session(request, session_key)
    user = request.user
    if input_username and user.username != input_username:
        log.warn(request.get_full_path())
        log.warn("Failed: Input username from the URL is %r but the request.user.username is %r" % (input_username, user.username))
        return HttpResponse('Access denied', status=401)

    if input_username:
        features, collections = get_user_data(user)
    elif input_uid:
        features, collections = get_data_for_feature(user, input_uid)
    elif input_shareuser and input_sharegroup:
        features, collections = get_shared_data(input_shareuser, input_sharegroup, user)
    else:
        raise Http404

    if not features and isinstance(collections, HttpResponse):
        return collections # We got an http error going on

    styles = get_styles(features,collections)

    t = get_template('kmlapp/base.kml')
    kml = t.render(Context({'user': user, 'features': features, 'collections': collections,
        'use_network_links': links, 'request_path': request.path, 'styles': styles, 
        'session_key': session_key, 'shareuser': input_shareuser, 'sharegroup': input_sharegroup}))

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
    
    from lingcod.features import groups_users_sharing_with 
    sharing_with = groups_users_sharing_with(user)

    t = get_template('kmlapp/shared.kml')
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
    features, collections = get_public_data()

    styles = get_styles(features,collections)

    # determine content types for sharing
    t = get_template('kmlapp/base.kml')
    kml = t.render(Context({'loggedin_user': request.user, 'user': request.user, 
        'features': features, 'collections': collections, 'styles': styles, 
        'use_network_links': True, 'request_path': request.path, 
        'session_key': session_key}))

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
