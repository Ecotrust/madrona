from django.http import HttpResponse
from django.shortcuts import render_to_response
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common.utils import load_session
from forms import UploadForm
from django.template import RequestContext


def load_single_shp(request, session_key):
    """
    GET returns a form to upload a zipped shp
    POST takes the zip, validates that it is a single-feature poly shp and returns KML
    """
    load_session(request, session_key)
    user = request.user
    if user.is_anonymous() or not user.is_authenticated():
        return HttpResponse('You must be logged in', status=401)

    form = UploadForm()
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)

        # Override the defulat form behavior and 
        # only allow single-feature polygon shps
        form.multi_feature = False
        form.supported_geomtypes = ['Polygon']

        if form.is_valid():
            layer = form.handle(request.FILES['file_obj'],user)
            response = render_to_response('loadshp/loadshp.kml', 
                    {'username': user.username, 
                    'session_key': session_key,
                    'layer': layer,
                    }, 
                    mimetype=mimetypes.KML
                )

            response['Content-Disposition'] = 'attachment; filename=loadshp_single.kml'
            return response
    elif request.method != 'GET':
        raise Exception("This URL does not support %s requests" % request.method)

    return render_to_response('loadshp/upload.html', RequestContext(request,{'form': form}))


