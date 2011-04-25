# Create your views here.
from lingcod.heatmap.models import create_heatmap
from lingcod.shapes.views import ShpResponder
from lingcod.common import default_mimetypes as mimetypes
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from lingcod.features import get_feature_by_uid, get_collection_models
from lingcod.features.models import PolygonFeature
import os

def overlap_geotiff(collection_uids, user=None):
    collections = [get_feature_by_uid(x) for x in collection_uids.split(',')]
    collections = [x for x in collections if x.__class__ in get_collection_models()]
    if len(collections) < 1:
        raise Http404

    filenames = []
    for collection in collections:
        viewable, response = collection.is_viewable(user)
        if user and not viewable:
            return response

        fs = collection.feature_set(recurse=True)
        poly_fs = [x for x in fs if isinstance(x,PolygonFeature)]
        unique_types = list(set([x.__class__ for x in poly_fs]))
        for model in unique_types:
            responder = ShpResponder(model.objects.filter(pk__in=[x.pk for x in poly_fs if x.__class__ == model]))
            responder.geo_field = 'geometry_final'
            fn = responder('return_file_not_response')
            filenames.append(fn)

    temp_geotiff = create_heatmap(filenames)
    return temp_geotiff
    
def overlap_geotiff_response(request, collection_uids):
    import cStringIO
    buff = cStringIO.StringIO()
    temp_geotiff = overlap_geotiff(collection_uids, request.user)
    if isinstance(temp_geotiff, HttpResponse):
        return temp_geotiff
    rfile = open(temp_geotiff,'rb')
    buff.write(rfile.read())
    buff.flush()
    stream = buff.getvalue()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(temp_geotiff)
    response['Content-length'] = str(len(stream))
    response['Content-Type'] = 'image/geotiffint16'
    response.write(stream)
    return response

def overlap_kmz_response(request, collection_uids):
    import cStringIO
    import shutil
    import tempfile

    buff = cStringIO.StringIO()
    temp_geotiff = overlap_geotiff(collection_uids, request.user)
    if isinstance(temp_geotiff, HttpResponse):
        return response
    
    tempdir = os.path.join(tempfile.gettempdir(),str(collection_uids.__hash__()))
    if os.path.exists(tempdir):
        shutil.rmtree(tempdir)
    os.mkdir(tempdir)
    outrgb = os.path.join(tempdir, "rgb.png")
    outvrt = os.path.join(tempdir, "rgb.vrt")
    outkmldir = os.path.join(tempdir, "kmlfiles")
    if os.path.exists(outkmldir):
        shutil.rmtree(outkmldir)
    os.mkdir(outkmldir)
    outkmz = os.path.join(tempdir, "array_overlap.kmz")

    # Convert to RGB 
    cmd = "pct2rgb.py -of PNG %s %s" % (temp_geotiff, outrgb)  
    print cmd
    print os.popen(cmd).read()

    # Assign a nodata value
    cmd = "gdal_translate -of vrt -a_nodata 0 %s %s" % (outrgb, outvrt)
    print cmd
    print os.popen(cmd).read()
         
    # Split into wgs84 tiles
    cmd = "gdal2tiles.py -k -z 6-10 -p geodetic %s %s" % (outvrt, outkmldir)
    print cmd
    print os.popen(cmd).read()

    # Zip up directory into a kmz
    print "Creating", outkmz
    from lingcod.common.utils import KMZUtil
    zu = KMZUtil()
    filename = outkmz
    os.chdir(outkmldir)
    directory = ""
    zu.toZip(directory, filename)

    if not os.path.exists(outkmz):
        return HttpResponse("KMZ creation error", status=500)
    rfile = open(outkmz,'rb')
    buff.write(rfile.read())
    buff.flush()
    stream = buff.getvalue()
    response = HttpResponse()
    response['Content-Disposition'] = 'attachment; filename=%s' % os.path.basename(outkmz)
    response['Content-length'] = str(len(stream))
    response['Content-Type'] = mimetypes.KMZ
    response.write(stream)
    return response


