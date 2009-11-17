from django.shortcuts import render_to_response
from lingcod.common import mimetypes
from django.contrib.auth.models import *
from lingcod.common import utils 

def get_mpa_data(user):
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
    user = request.user
    if user.username != input_username or user.is_anonymous or not user.is_authenticated:
        # TODO return HttpResponse('You must be logged in.', status=401)
        # right now this assumes a fixture with username dummy exists
        user = User.objects.get(username="dummy")
    return user

def create_mpa_kml(request, input_username):
    user = get_user(request,input_username)
    shapes, designations = get_mpa_data(user)
    response = render_to_response('main.kml', {'shapes': shapes, 'designations': designations}, mimetype=mimetypes.KML)
    response['Content-Type'] = mimetypes.KML
    response['Content-Disposition'] = 'attachment;filename=%s_mpa.kml' % user.username
    return response
