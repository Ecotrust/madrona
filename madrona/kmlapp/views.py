from django.shortcuts import render
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from madrona.common import default_mimetypes as mimetypes
from madrona.common import utils
from django.http import Http404
from madrona.common.utils import load_session, get_logger
from django.contrib.gis.db import models
from django.core.exceptions import FieldError
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from madrona.features import get_feature_models, get_collection_models, get_feature_by_uid
from madrona.features.models import FeatureCollection, Feature
try:
    set
except NameError:
    from sets import Set as set

log = get_logger()

def get_styles(features, collections, links=True):
    """
    Based on which features and collection are provided,
    the styles for all features are determined here
    """
    models = []
    models.extend([f.kml_style for f in features])
    models.extend([c.kml_style for c in collections])
    if not links:
        # Collections will be represented by Folders, not NetworkLinks
        # So every feature n the entire tree will be in this KML Doc
        # We need to recurse down to determine what's in there
        for c in collections:
            children = c.feature_set(recurse=True)
            models.extend([child.kml_style for child in children])
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

    for fmodel in get_feature_models():
        unattached = list(fmodel.objects.filter(user=user, content_type=None, object_id=None))
        toplevel_features.extend(unattached)

    for cmodel in get_collection_models():
        collections_top = list(cmodel.objects.filter(user=user, content_type=None, object_id=None))
        toplevel_collections.extend(collections_top)

    return toplevel_features, toplevel_collections

def get_data_for_feature(user, uid):
    try:
        f = get_feature_by_uid(uid)
    except:
        return False, HttpResponse("Feature %s does not exist" % uid, status=404)

    viewable, response = f.is_viewable(user)
    if not viewable:
        return viewable, response

    features = []
    collections = []

    if isinstance(f, FeatureCollection):
        obj_id = f.pk
        ct = ContentType.objects.get_for_model(f.__class__)
        for fmodel in get_feature_models():
            unattached = list(fmodel.objects.filter(content_type=ct,object_id=obj_id))
            features.extend(unattached)

        for cmodel in get_collection_models():
            collections_top = list(cmodel.objects.filter(content_type=ct,object_id=obj_id))
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

    for fmodel in get_feature_models():
        unattached = list(fmodel.objects.filter(sharing_groups__in=public_groups))
        features.extend(unattached)

    for cmodel in get_collection_models():
        collections_top = list(cmodel.objects.filter(sharing_groups__in=public_groups))
        collections.extend(collections_top)

    return features, collections

def get_shared_data(shareuser, sharegroup, user):
    sg = Group.objects.get(pk=sharegroup)
    su = User.objects.get(pk=shareuser)

    features = []
    collections = []

    for fmodel in get_feature_models():
        # Find top level features shared with user
        # top-level == not belonging to any collections
        # have to use content_type and object_id fields to determine
        unattached = list(
                fmodel.objects.shared_with_user(user,filter_groups=[sg])
                 .filter(user=su, content_type=None,object_id=None)
        )
        features.extend(unattached)

    for cmodel in get_collection_models():
        collections_top = list(
                cmodel.objects.shared_with_user(user,filter_groups=[sg])
                 .filter(user=su, content_type=None,object_id=None)
        )
        collections.extend(collections_top)

    return features, collections

def create_kmz(kml, zippath):
    """
    Given a KML string and a "/" seperated path like "FOLDERNAME/doc.kml",
    creates a zipped KMZ archive buffer that can be written directly to a
    django response object
    """
    import tempfile
    from io import StringIO, BytesIO
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
    try:
        strbuffer = StringIO()
        with zipfile.ZipFile(strbuffer,'w',zipfile.ZIP_DEFLATED) as strzipout:
            strzipout.write(kmlfile.name, zippath.encode('ascii'))
        kmzbuffer = strbuffer
    except TypeError as e:
        bytbuffer = BytesIO()
        with zipfile.ZipFile(bytbuffer,'w',zipfile.ZIP_DEFLATED) as bytzipout:
            bytzipout.write(kmlfile.name, zippath)
        kmzbuffer = bytbuffer

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
def create_kml(request, input_username=None, input_uid=None,
        input_shareuser=None, input_sharegroup=None, links=False, kmz=False,
        session_key='0'):
    """
    Returns a KML/KMZ containing Feautures/FeatureCollections owned by user
    """
    load_session(request, session_key)
    user = request.user
    if input_username and user.username != input_username:
        log.warn("Input username from URL is %r but request.user.username is %r" % (input_username, user.username))
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

    styles = get_styles(features,collections,links)

    t = get_template('kmlapp/myshapes.kml')
    context = {
                'user': user,
                'features': features,
                'collections': collections,
                'use_network_links': links,
                'request_path': request.path,
                'styles': styles,
                'session_key': session_key,
                'shareuser': input_shareuser,
                'sharegroup': input_sharegroup,
                'feature_id': input_uid,
                }
    kml = t.render(context)
    mime = mimetypes.KML
    if kmz:
        mime = mimetypes.KMZ
        kml = create_kmz(kml, 'mm/doc.kml')
    response = HttpResponse(kml, content_type=mime)
    response['Content-Disposition'] = 'attachment'
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

    from madrona.features import groups_users_sharing_with
    sharing_with = groups_users_sharing_with(user)

    t = get_template('kmlapp/shared.kml')
    context = {
        'user': request.user,
        'groups_users': sharing_with,
        'request_path': request.path,
        'session_key': session_key
    }
    kml = t.render(context)

    mime = mimetypes.KML
    if kmz:
        mime = mimetypes.KMZ
        kml = create_kmz(kml, 'mm/doc.kml')
    response = HttpResponse(kml, content_type=mime)
    response['Content-Disposition'] = 'attachment'
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
    t = get_template('kmlapp/public.kml')
    kml = t.render({'loggedin_user': request.user, 'user': request.user,
        'features': features, 'collections': collections, 'styles': styles,
        'use_network_links': True, 'request_path': request.path,
        'session_key': session_key})

    mime = mimetypes.KML
    if kmz:
        mime = mimetypes.KMZ
        kml = create_kmz(kml, 'mm/doc.kml')
    response = HttpResponse(kml, content_type=mime)
    response['Content-Disposition'] = 'attachment'
    return response
