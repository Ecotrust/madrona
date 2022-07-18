from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render
from django.db import connection
from madrona.common import default_mimetypes as mimetypes
from madrona.common import utils
from madrona.staticmap.models import MapConfig
from madrona.features import get_feature_models, get_collection_models, get_feature_by_uid, get_model_by_uid
from madrona.features.models import FeatureCollection, SpatialFeature, PointFeature, PolygonFeature, LineFeature
from madrona.common.utils import get_logger
from django.template.defaultfilters import slugify
log = get_logger()

try:
    settings_dbname = settings.DATABASES['default']['NAME']
except:
    settings_dbname = settings.DATABASE_NAME


def get_features(uids,user):
    """
    Returns list of tuples representing mapnik layers
    Tuple => (model_class, [pks])
    Note: currently just a single pk per 'layer' which is
    incredibly inefficient but the only way to ensure
    proper layer ordering (??).
        features = [ (Mpa, [49, 50]),
                    (Pipeline, [32, 31]),
                    (Shipwreck, [32, 31])
                ]
    """
    feature_models = get_feature_models()
    collection_models = get_collection_models()
    features = [] # list of tuples => (model, [pks])
    for uid in uids:
        log.debug("processing uid %s" % uid)
        applabel, modelname, pk = uid.split('_')
        model = get_model_by_uid("%s_%s" % (applabel,modelname))
        feature = get_feature_by_uid(uid)

        if user:
            viewable, response = feature.is_viewable(user)
            if not viewable:
                continue

        if model in collection_models:
            collection = get_feature_by_uid(uid)
            if user:
                viewable, response = collection.is_viewable(user)
                if not viewable:
                    continue
            all_children = collection.feature_set(recurse=True)
            children = [x for x in all_children if x.__class__ in feature_models]
            for child in children:
                features.append((child.__class__,[child.pk]))
        else:
            features.append((model,[int(pk)]))

    return features

def auto_extent(features,srid=settings.GEOMETRY_CLIENT_SRID):
    """
    Given a set of staticmap features,
    returns the bounding box required to zoom into those features.
    Includes a configurable edge buffer
    """
    minx = 99999999.0
    miny = 99999999.0
    maxx = -99999999.0
    maxy = -99999999.0
    for model, pks in features:
        try:
            geomfield = model.mapnik_geomfield()
        except AttributeError:
            geomfield = 'geometry_final'

        try:
            ugeom = model.objects.filter(pk__in=pks).collect(field_name=geomfield).transform(srid,clone=True)
            bbox = ugeom.extent
            if bbox[0] < minx:
                minx = bbox[0]
            if bbox[1] < miny:
                miny = bbox[1]
            if bbox[2] > maxx:
                maxx = bbox[2]
            if bbox[3] > maxy:
                maxy = bbox[3]
        except TypeError as e:
            log.error("Failed to get extent for %r with pks %r; Exception: \n%s" % (model, pks, e))
            pass

    width = maxx - minx
    height = maxy - miny
    buffer = .15
    # if width and height are 0 (such as for a point geom)
    # we need to take a stab a reasonable value
    if width == 0:
        if bbox[2] <= 180.1:
            width = 0.1
        else:
            width = 1000
    if height == 0:
        if bbox[3] <= 90.1:
            height = 0.1
        else:
            height = 1000

    # If the following settings variables are not defined (or set to None), then the original method
    # for determining width_buffer and heigh_buffer is used
    try:
        if settings.STATICMAP_WIDTH_BUFFER is not None and settings.STATICMAP_HEIGHT_BUFFER is not None:
            width_buffer = settings.STATICMAP_WIDTH_BUFFER
            height_buffer = settings.STATICMAP_HEIGHT_BUFFER
        else:
            raise AttributeError
    except AttributeError:
        width_buffer = width * buffer
        height_buffer = height * buffer

    return minx - width_buffer, miny - height_buffer, maxx + width_buffer, maxy + height_buffer


def staticmap_link(request, instances, map_name="default"):
    """
    Generic link version of the staticmap view
    """
    width, height = None, None
    uids = [i.uid for i in instances]
    filename = '_'.join([slugify(i.name) for i in instances])
    autozoom = settings.STATICMAP_AUTOZOOM
    bbox = None
    show_extent = False

    img = draw_map(uids, request.user, width, height, autozoom, bbox, show_extent, map_name)

    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png'
    response['Content-Disposition'] = 'attachment; filename=%s.png' % filename
    response.write(img)
    return response


def show(request, map_name="default"):
    # Grab the image dimensions
    try:
        width = int(request.REQUEST['width'])
        height = int(request.REQUEST['height'])
    except:
        # fall back on defaults
        width, height = None, None

    if 'uids' in request.REQUEST:
        uids = str(request.REQUEST['uids']).split(',')
    else:
        uids = []

    if "autozoom" in request.REQUEST and request.REQUEST['autozoom'].lower() == 'true':
        autozoom = True
    else:
        autozoom = False

    if "bbox" in request.REQUEST:
        bbox = request.REQUEST['bbox']
    else:
        bbox = None

    if "show_extent" in request.REQUEST and request.REQUEST['show_extent'].lower() == 'true':
        show_extent = True
    else:
        show_extent = False

    img = draw_map(uids, request.user, width, height, autozoom, bbox, show_extent, map_name)

    if 'attachment' in request.REQUEST and request.REQUEST['attachment'].lower() == 'true':
        attach = True
    else:
        attach = False

    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png'
    if attach:
        response['Content-Disposition'] = 'attachment; filename=madrona.png'
    response.write(img)

    return response

def draw_map(uids, user, width, height, autozoom=False, bbox=None, show_extent=False, map_name='default'):
    """Display a map with the study region geometry.  """
    # if testing via django unit tests, close out the connection
    conn = connection.settings_dict
    testing = False
    if conn['NAME'] != settings_dbname:
        testing = True

    map = get_object_or_404(MapConfig,mapname=map_name)
    if not width:
        width = map.default_width
    if not height:
        height = map.default_height
    mapfile = str(map.mapfile.path)

    # load_map is NOT thread safe (?)
    # load_map_from_string appears to work
    #mapnik.load_map(m, mapfile)
    xmltext = open(mapfile).read()
    # Replace mediaroot
    xmltext = xmltext.replace("[[MEDIA_ROOT]]",settings.MEDIA_ROOT)
    log.debug("Completed load_map_from_string(), Map object is %r" % m)

    # Create the mapnik layers
    features = get_features(uids,user)
    for model, pks in features:

        if geomfield not in [str(x.name) for x in model._meta.fields]:
            continue
    # Grab the bounding coordinates and set them if specified
    # first, assume default image extent
    x1, y1 = map.default_x1, map.default_y1
    x2, y2 = map.default_x2, map.default_y2

    if not bbox and autozoom and features and len(features) > 0:
        x1, y1, x2, y2 = auto_extent(features, map.default_srid)
    if bbox:
        try:
            x1, y1, x2, y2 = [float(x) for x in bbox.split(',')]
        except:
            pass


    if show_extent and features and len(features) > 0:
        # Shows a bounding box for the extent of all specified features
        # Useful for overview maps
        x1, y1, x2, y2 = auto_extent(features, map.default_srid)

        ps.fill_opacity = 0.8
        r.symbols.append(ps)
        r.symbols.append(ls)
        extent_style.rules.append(r)
        m.append_style('extent_style', extent_style)
        lyr.styles.append('extent_style')
        m.layers.append(lyr)

    # Render image and send out the response
    m.zoom_to_box(bbox)

    img = draw.tostring('png')

    if testing:
        del m

    return img
