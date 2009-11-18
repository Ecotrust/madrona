from django.shortcuts import render_to_response
from django.contrib.auth.models import *
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from lingcod.common import mimetypes
from lingcod.common import utils 

def get_mpa_data(user):
    """
    Organizes user's MPAs into arrays and provides their designations.
    Just basically a data structure manipulation on the queryset.
    """
    from lingcod.mpa.models import MpaDesignation
    Mpa = utils.get_mpa_class()

    mpas = Mpa.objects.filter(user=user)
    shapes = {'Unattached':[]}
    for mpa in mpas:
        if not mpa.array:
            shapes['Unattached'].append(mpa)
        else:
            if mpa.array.name in shapes:
                shapes[mpa.array.name].append(mpa)
            else:
                shapes[mpa.array.name] = [mpa]
    designations = MpaDesignation.objects.all()
    return shapes, designations

def get_user(request, input_username):
    """
    Logic to determine what user's KMLs get returned
    """
    user = request.user
    if user.username != input_username or user.is_anonymous or not user.is_authenticated:
        # TODO return HttpResponse('You must be logged in.', status=401)
        # right now this assumes a fixture with username dummy exists
        user = User.objects.get(username="dummy")
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
    zipout.write(kmlfile.name, zippath) 
    zipout.close()
    # close out the tempfile
    kmlfile.close()
    # grab the content of the stringIO buffer
    kmz = kmzbuffer.getvalue()
    # close out the stringIO buffer
    kmzbuffer.close()
    return kmz

def create_mpa_kml(request, input_username):
    """
    Returns a KML of users MPAs (organized into folder by array)
    """
    user = get_user(request,input_username)
    shapes, designations = get_mpa_data(user)
    response = render_to_response('main.kml', {'shapes': shapes, 'designations': designations}, mimetype=mimetypes.KML)
    response['Content-Type'] = mimetypes.KML
    response['Content-Disposition'] = 'attachment;filename=%s_mpa.kml' % user.username
    return response


def create_mpa_kmz(request, input_username):
    """
    Returns a KMZ of users MPAs (organized into folder by array)
    """
    user = get_user(request,input_username)
    shapes, designations = get_mpa_data(user)

    t = get_template('main.kml')
    kml = t.render(Context({'shapes': shapes, 'designations': designations}))
    kmz = create_kmz(kml, '%s_mpa/doc.kml' % user.username)

    response = HttpResponse()
    response['Content-Type'] = mimetypes.KMZ
    response['Content-Disposition'] = 'attachment;filename=%s_mpa.kmz' % user.username
    response.write(kmz)
    return response
