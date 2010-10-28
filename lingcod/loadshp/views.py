from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.conf import settings
from django.utils import simplejson
from django.template import Context, RequestContext
from django.template.loader import get_template
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common.utils import kml_errors
from forms import UploadForm


def load_single_shp(request):
    """
    GET returns a form to upload a zipped shp
    POST takes the zip, validates that it is a single-feature poly shp and returns KML 
    """
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
            g = layer[0].geom
            g.transform_to(4326)
            geoms = [g]
            t = get_template('loadshp/loadshp.kml')
            kml = t.render(Context({'username': user.username, 'geoms': geoms}))
            json = simplejson.dumps({'input_kml': kml, 'status':'success'})
            # Jquery Form plugin requires that we wrap this in a textarea 
            # otherwise it mangles the kml  
            return HttpResponse('<textarea>'+json+'</textarea>',mimetype="text/html")
        else:
            json = simplejson.dumps({'error_html': form.errors['file_obj'][0], 'status':'errors'})
            return HttpResponse('<textarea>'+json+'</textarea>',mimetype="text/html")

    elif request.method == 'GET':
        return render_to_response('loadshp/upload.html', RequestContext(request,{'form': form,'action':request.path}))

    else:
        raise Exception("This URL does not support %s requests" % request.method)



