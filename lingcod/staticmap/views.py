try:
	import mapnik
except:
	import mapnik2 as mapnik
import settings
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from lingcod.common import default_mimetypes as mimetypes
from lingcod.common import utils
from lingcod.staticmap.models import MapConfig
from lingcod.features import get_feature_models, get_collection_models, get_feature_by_uid, get_model_by_uid
from lingcod.features.models import SpatialFeature, PointFeature, PolygonFeature, LineFeature
from djmapnik.adapter import PostgisLayer 
from lingcod.common.utils import get_logger
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
    if not srid:
        srid = settings.GEOMETRY_CLIENT_SRID # Assume latlong if none
    
    minx = 361.0
    miny = 361.0
    maxx = -361.0
    maxy = -361.0
    for model, pks in features:
        ugeom = model.objects.filter(pk__in=pks).unionagg().transform(srid,clone=True)
        bbox = ugeom.extent
        if bbox[0] < minx: minx = bbox[0]
        if bbox[1] < miny: miny = bbox[1]
        if bbox[2] > maxx: maxx = bbox[2]
        if bbox[3] > maxy: maxy = bbox[3]
    
    width = maxx - minx
    height = maxy - miny  
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
        
    return minx-width_buffer, miny-height_buffer, maxx+width_buffer, maxy+height_buffer

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

def staticmap_link(request, instances, map_name="default"):
    """
    Generic link version of the staticmap view
    """
    width, height = None, None
    uids = [i.uid for i in instances]
    filename = '_'.join([slugify(i.name) for i in instances])
    autozoom = False
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
        response['Content-Disposition'] = 'attachment; filename=marinemap.png'
    response.write(img)

    return response

def draw_map(uids, user, width, height, autozoom=False, bbox=None, show_extent=False, map_name='default'):
    """Display a map with the study region geometry.  """
    map = get_object_or_404(MapConfig,mapname=map_name)
    if not width:
        width = map.default_width
    if not height: 
        height = map.default_height
    mapfile = str(map.mapfile.path)
    
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
    features = get_features(uids,user)
    for model, pks in features:
        if issubclass(model, SpatialFeature):
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
    
    if autozoom and features and len(features)>0:
        x1, y1, x2, y2 = auto_extent(features, map.default_srid)
    if bbox:
        try:
            x1, y1, x2, y2 = [float(x) for x in bbox.split(',')]
        except:
            pass

    bbox = mapnik.Envelope(mapnik.Coord(x1,y1), mapnik.Coord(x2,y2))

    if show_extent and features and len(features)>0:
        # Shows a bounding box for the extent of all specified features
        # Useful for overview maps
        x1, y1, x2, y2 = auto_extent(features, map.default_srid)

        ps = mapnik.PolygonSymbolizer(mapnik.Color('#ffffff'))
        ps.fill_opacity = 0.8
        ls = mapnik.LineSymbolizer(mapnik.Color('#ff0000'),2.0)
        r = mapnik.Rule()
        r.symbols.append(ps)
        r.symbols.append(ls)
        extent_style = mapnik.Style()
        extent_style.rules.append(r)
        m.append_style('extent_style', extent_style)
        lyr = mapnik.Layer("Features Extent")
        bbox_sql = """
        (select 1 as id, st_setsrid(st_makebox2d(st_point(%s,%s),st_point(%s,%s)), %s) as geometry_final) as aoi
        """ % (x1,y1,x2,y2,map.default_srid)
        lyr.datasource = mapnik.PostGIS(host=connection.settings_dict['HOST'],
                user=connection.settings_dict['USER'],
                password=connection.settings_dict['PASSWORD'],
                dbname=connection.settings_dict['NAME'], 
                table=bbox_sql,
                geometry_field='geometry_final',
                estimate_extent='False',
                extent='%s,%s,%s,%s' % (x1,y1,x2,y2))
        lyr.styles.append('extent_style')
        m.layers.append(lyr)
    
    # Render image and send out the response
    m.zoom_to_box(bbox)

    mapnik.render(m, draw)
    img = draw.tostring('png')

    # if testing via django unit tests, close out the connection
    conn = connection.settings_dict
    if conn['NAME'] != settings_dbname:
        del m

    return img

