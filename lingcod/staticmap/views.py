import mapnik
import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common import utils
from lingcod.staticmap.models import MapConfig
from lingcod.features import get_feature_models, get_collection_models, get_feature_by_uid, get_model_by_uid
from lingcod.features.models import PointFeature, PolygonFeature, LineFeature
from djmapnik.adapter import PostgisLayer 
from lingcod.common.utils import get_logger
log = get_logger()

try:
    settings_dbname = settings.DATABASES['default']['NAME']
except:
    settings_dbname = settings.DATABASE_NAME

feature_models = get_feature_models()
collection_models = get_collection_models()

def get_features(request):
    """ 
    Returns list of tuples representing mapnik layers
    Tuple => (model_class, [pks])
    Note: currently just a single pk per 'layer' which is
    incredibly inefficient but the best way to ensure 
    proper layer ordering.
        from mlpa.models import Mpa
        from mlpa.models import Pipeline
        from mlpa.models import Shipwreck
        features = [ (Mpa, [49, 50]),
                    (Pipeline, [32, 31]),
                    (Shipwreck, [32, 31])
                ]
    """
    features = [] # list of tuples => (model, [pks])
    if 'uids' in request.REQUEST: 
        uids = str(request.REQUEST['uids']).split(',')
        for uid in uids:
            log.debug("processing uid %s" % uid)
            applabel, modelname, pk = uid.split('_')
            model = get_model_by_uid("%s_%s" % (applabel,modelname))
            feature = get_feature_by_uid(uid)

            viewable, response = feature.is_viewable(request.user)
            if not viewable:
                continue

            if model in collection_models:
                collection = get_feature_by_uid(uid)
                viewable, response = collection.is_viewable(request.user)
                if not viewable:
                    continue
                all_children = collection.feature_set(recurse=True)
                children = [x for x in all_children if x.__class__ in feature_models]
                for child in children:
                    features.append((child.__class__,[child.pk]))
            else:
                features.append((model,[pk]))

    return features

def auto_extent(mpa_ids,srid=settings.GEOMETRY_CLIENT_SRID):
    if not srid:
        srid = settings.GEOMETRY_CLIENT_SRID # Assume latlong if none
    # would be nice to just do a transform().extent() but this doesnt work - geodjango bug
    ugeom = mpa_class.objects.filter(pk__in=mpa_ids).unionagg().transform(srid,clone=True)
    bbox = ugeom.extent
    
    width = bbox[2]-bbox[0]
    height = bbox[3]-bbox[1]
    buffer = .15
    
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
        
    return bbox[0]-width_buffer, bbox[1]-height_buffer, bbox[2]+width_buffer, bbox[3]+height_buffer

def get_designation_style(mpas):
    mpa_filter_string = get_mpa_filter_string(mpas)
    # Override the mpa_style according to MPA designations
    s = mapnik.Style()
    designations = MpaDesignation.objects.all()
    for d in designations:
        r = mapnik.Rule()
        fill = utils.hex8_to_rgba(d.poly_fill_color)
        outl = utils.hex8_to_rgba(d.poly_outline_color)
        r.symbols.append(mapnik.PolygonSymbolizer(mapnik.Color('rgb(%d,%d,%d)' % (fill[0],fill[1],fill[2]))))
        r.symbols.append(mapnik.LineSymbolizer(mapnik.Color('rgb(%d,%d,%d)' % (outl[0],outl[1],outl[2])),0.8))
        r.filter = mapnik.Filter("[designation_id] = %d and (%s)" % (d.id, mpa_filter_string)) 
        s.rules.append(r)
    # And for null designations
    r = mapnik.Rule()
    #the following colors may be overridden in mapfile's mpa_style section
    r.symbols.append(mapnik.PolygonSymbolizer(mapnik.Color('rgb(150,0,0)'))) 
    r.symbols.append(mapnik.LineSymbolizer(mapnik.Color('rgb(255,255,0)'),0.2))
    if len(designations) > 0:
        r.filter = mapnik.Filter("[designation_id] = '' and (%s)" % mpa_filter_string)
    s.rules.append(r)
    return s

def draw_to_response(m, draw, request):
    mapnik.render(m, draw)
    img = draw.tostring('png')
    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png' 
    if 'attachment' in request.REQUEST and request.REQUEST['attachment'].lower() == 'true':
        response['Content-Disposition'] = 'attachment; filename=marinemap.png'
    response.write(img)
    return response

def show(request, map_name='default'):
    """Display a map with the study region geometry.  """
    map = get_object_or_404(MapConfig,mapname=map_name)
    mapfile = str(map.mapfile.path)
    
    # Grab the image dimensions
    try:
        width = int(request.REQUEST['width'])
        height = int(request.REQUEST['height'])
    except:
        # fall back on defaults
        width, height = map.default_width, map.default_height

    # Create a blank image and map
    draw = mapnik.Image(width,height)
    m = mapnik.Map(width,height)

    # load_map is NOT thread safe (?)
    # load_map_from_string appears to work
    #mapnik.load_map(m, mapfile)
    xmltext = open(mapfile).read()
    mapnik.load_map_from_string(m, xmltext)
    log.debug("Completed load_map_from_string(), Map object is %r" % m)

    # Create the mapnik layers
    for model, pks in get_features(request):
        style = model.mapnik_style()
        style_name = str('%s_style' % model.model_uid()) # tsk mapnik cant take unicode
        m.append_style(style_name, style)
        adapter = PostgisLayer(model.objects.filter(pk__in=pks), field_name="geometry_final")
        lyr = adapter.to_mapnik()
        lyr.styles.append(style_name)
        m.layers.append(lyr)

    # Grab the bounding coordinates and set them if specified
    # first, assume default image extent
    x1, y1 = map.default_x1, map.default_y1
    x2, y2 = map.default_x2, map.default_y2
    
    if "autozoom" in request.REQUEST:
        # TODO - not supported with CMS
        if request.REQUEST['autozoom'].lower() == 'true' and mpas and len(mpas)>0:
            x1, y1, x2, y2 = auto_extent(mpas, map.default_srid)
    elif "bbox" in request.REQUEST:
        try:
            x1, y1, x2, y2 = [float(x) for x in str(request.REQUEST['bbox']).split(',')]
        except:
            pass

    bbox = mapnik.Envelope(mapnik.Coord(x1,y1), mapnik.Coord(x2,y2))
    m.zoom_to_box(bbox)
    
    # Render image and send out the response
    response = draw_to_response(m, draw, request)

    # if testing via django unit tests, close out the connection
    conn = connection.settings_dict
    if conn['NAME'] != settings_dbname:
        del m

    return response
