from django.shortcuts import render_to_response
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse, Http404
from lingcod.common import mimetypes
from lingcod.common import utils 
from lingcod.mpa.models import MpaDesignation
from django.http import Http404

def get_user_mpa_data(user):
    """
    Organizes user's MPAs into arrays and provides their designations.
    Just basically a data structure manipulation on the queryset.

    The template expects something like:
     {'array name + id': {'array': array_object, 'mpas': [mpa1, mpa2] } }
    """
    Mpa = utils.get_mpa_class()

    mpas = Mpa.objects.filter(user=user)
    unattached = utils.get_array_class()(name='Unattached')
    shapes = {'Unattached': {'array': unattached, 'mpas':[]} }
    for mpa in mpas:
        if not mpa.array:
            shapes['Unattached']['mpas'].append(mpa)
        else:
            array_nameid = "%s_%d" % (mpa.array.name, mpa.array.id)
            if mpa.array.name in shapes.keys():
                shapes[array_nameid]['mpas'].append(mpa)
            else:
                shapes[array_nameid] = {'array': mpa.array, 'mpas':[mpa]}
    for array in utils.get_array_class().objects.empty():
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

    # TODO: sharing and permissions
    try:
        the_array = MpaArray.objects.get(id=input_array_id)
    except:
        raise Http404
    mpas = the_array.mpa_set
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

    # TODO: sharing and permissions
    try:
        mpa = Mpa.objects.get(id=input_mpa_id)
    except:
        raise Http404
    if mpa.array:
        array_nameid = "%s_%d" % (the_array.name, the_array.id)
        shapes = {array_nameid: {'array':mpa.array, 'mpas': [mpa]} }
    else:
        unattached = utils.get_array_class()(name='Unattached')
        shapes = {'Unattached': {'array': unattached, 'mpas':[mpa]} }
    designations = [mpa.designation]
    return shapes, designations

def get_user(request, input_username):
    """
    Logic to determine what user's KMLs get returned
    """
    user = request.user
    if user.username != input_username or user.is_anonymous or not user.is_authenticated:
        # TODO return HttpResponse('You must be logged in.', status=401)
        # right now this assumes a fixture with username default_user exists
        user = User.objects.get(username="default_user")
    return user

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
    kmlfile.write(kml)
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

def create_mpa_kml(request, input_username=None, input_array_id=None, input_mpa_id=None):
    """
    Returns a KML containing MPAs (organized into folders by array)
    """
    user = get_user(request,input_username)
    if input_username:
        shapes, designations = get_user_mpa_data(user)
    elif input_array_id:
        shapes, designations = get_array_mpa_data(user, input_array_id)
    elif input_mpa_id:
        shapes, designations = get_single_mpa_data(user, input_mpa_id)
    else:
        raise 404

    response = render_to_response('placemark.kml', {'shapes': shapes, 'designations': designations}, mimetype=mimetypes.KML)
    response['Content-Type'] = mimetypes.KML
    response['Content-Disposition'] = 'attachment' 
    return response


def create_mpa_kmz(request, input_username=None, input_array_id=None, input_mpa_id=None):
    """
    Returns a KMZ containing MPAs (organized into folders by array)
    """
    user = get_user(request,input_username)
    if input_username:
        shapes, designations = get_user_mpa_data(user)
    elif input_array_id:
        shapes, designations = get_array_mpa_data(user, input_array_id)
    elif input_mpa_id:
        shapes, designations = get_single_mpa_data(user, input_mpa_id)
    else:
        raise 404

    t = get_template('placemark.kml')
    kml = t.render(Context({'shapes': shapes, 'designations': designations}))
    kmz = create_kmz(kml, 'mpa/doc.kml')

    response = HttpResponse()
    response['Content-Type'] = mimetypes.KMZ
    response['Content-Disposition'] = 'attachment'
    response.write(kmz)
    return response

def create_mpa_kml_links(request, input_username):
    """
    Returns a KML containing MPAs owned by a user, each array is a network link to an array.kml 
    """
    user = get_user(request,input_username)
    shapes, designations = get_user_mpa_data(user)
    response = render_to_response('placemark_links.kml', {'shapes': shapes, 'designations': designations}, mimetype=mimetypes.KML)
    response['Content-Type'] = mimetypes.KML
    response['Content-Disposition'] = 'attachment' 
    return response

def create_mpa_kmz_links(request, input_username):
    """
    Returns a KMZ containing MPAs owned by a user, each array is a network link to an array.kml 
    """
    user = get_user(request,input_username)
    shapes, designations = get_user_mpa_data(user)

    t = get_template('placemark_links.kml')
    kml = t.render(Context({'shapes': shapes, 'designations': designations}))
    kmz = create_kmz(kml, 'mpa/doc.kml')

    response = HttpResponse()
    response['Content-Type'] = mimetypes.KMZ
    response['Content-Disposition'] = 'attachment'
    response.write(kmz)
    return response
