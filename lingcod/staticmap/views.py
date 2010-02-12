from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden, Http404
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from lingcod.common import mimetypes, utils
from lingcod.mpa.models import MpaDesignation

import settings

from lingcod.staticmap.models import *

def show(request, map_name='default'):
    """Display a map with the study region geometry.  """
    maps = get_object_or_404(MapConfig,mapname=map_name)
    mapfile = str(maps.mapfile.path)
    mpa_class = utils.get_mpa_class()
     
    # Grab the image dimensions
    try:
        width = int(request.REQUEST['width'])
        height = int(request.REQUEST['height'])
    except:
        # fall back on defaults
        width, height = maps.default_width, maps.default_height

    # Create a blank image
    import mapnik
    draw = mapnik.Image(width,height)
    m = mapnik.Map(width,height)

    # Replace local settings-specific variables using keywords in mapnik mapfile
    # Uses ALL_CAPS keywords in the mapfile
    xmltext = open(mapfile).read()

    # get a list of the MPA ids to display
    try:
        mpas = str(request.REQUEST['mpas']).split(',')
        # make sure all given mpas are integers
        mpas = [int(x) for x in mpas if x.isdigit()]
    except KeyError:
        # If MPAs are not specified, don't render ANY of them
        mpas = []

    # If an array is specified, it's mpas are appended to the mpa list
    try:
        input_array_id = request.REQUEST['array']
        # Find that array object and get all associated mpas
        MpaArray = utils.get_array_class()
        the_array = MpaArray.objects.get(id=input_array_id)
        mpaids = [x.id for x in the_array.mpa_set]
        for mpaid in mpaids:
            mpas.append(mpaid)
    except:
        pass

    # Now that we have a list of requested mpas, lets make sure 
    # that the user actually has permissions to view them all
    # if any one fails, 403 or 404 will be raised
    user = request.user
    from lingcod.sharing.utils import get_viewable_object_or_respond 
    for pk in mpaids:
        # Does it even exist?
        try:
            obj = mpa_class.objects.get(pk=pk)
        except:
            raise Http404

        obj = None
        try:
            # Next see if user owns it
            obj = mpa_class.objects.get(pk=pk, user=user)
        except:
            try: 
                # ... finally see if its shared with the user
                obj = mpa_class.objects.shared_with_user(user).get(pk=pk)
            except mpa_class.DoesNotExist:
                return HttpResponse("Access denied", status=403)


    # construct filter and replace the MPA_FILTER tag
    mpa_queries = ['[id] = %d' % x for x in mpas] 
    mpa_filter_string = " or ".join(mpa_queries)
    xmltext = xmltext.replace("MPA_FILTER", mpa_filter_string)

    # Assume MEDIA_ROOT and DATABASE_NAME are always defined
    xmltext = xmltext.replace("MEDIA_ROOT",settings.MEDIA_ROOT)
    xmltext = xmltext.replace("GEOMETRY_DB_SRID",str(settings.GEOMETRY_DB_SRID))

    # Replace table names for mpas and mpaarrays
    xmltext = xmltext.replace("MM_MPA", str(mpa_class._meta.db_table))

    # Deal with deprecated connection settings 
    # (http://docs.djangoproject.com/en/dev/ref/settings/#deprecated-settings)
    # Maintain compatibility with django pre-1.2
    conn = connection.settings_dict
    try:
        DB_NAME = conn['NAME']
        DB_USER = conn['USER']
        DB_PASSWORD = conn['PASSWORD']
        DB_HOST = conn['HOST']
    except:
        DB_NAME = conn['DATABASE_NAME']
        DB_USER = conn['DATABASE_USER']
        DB_PASSWORD = conn['DATABASE_PASSWORD']
        DB_HOST = conn['DATABASE_HOST']

    connection_string = ""
    connection_string += "<Parameter name='dbname'>%s</Parameter>" % DB_NAME
    connection_string += "<Parameter name='user'>%s</Parameter>" % DB_USER
    connection_string += "<Parameter name='password'>%s</Parameter>" % DB_PASSWORD
    connection_string += "<Parameter name='host'>%s</Parameter>" % DB_HOST

    # if testing via django unit tests, close out the connection
    if DB_NAME != settings.DATABASE_NAME:
        connection_string += "<Parameter name='persist_connection'>false</Parameter>"

    xmltext = xmltext.replace("DATABASE_CONNECTION",connection_string)


    mapnik.load_map_from_string(m,xmltext)

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
    r.symbols.append(mapnik.PolygonSymbolizer(mapnik.Color('rgb(%d,%d,%d)' % (fill[0],fill[1],fill[2]))))
    r.symbols.append(mapnik.LineSymbolizer(mapnik.Color('rgb(%d,%d,%d)' % (outl[0],outl[1],outl[2])),0.8))
    r.filter = mapnik.Filter("[designation_id] = '' and (%s)" % mpa_filter_string)
    s.rules.append(r)

    m.append_style('mpa_style',s)
     
    # Grab the bounding coordinates and set them if specified
    try:
        x1, y1, x2, y2 = [float(x) for x in str(request.REQUEST['bbox']).split(',')]
    except:
        # fall back on default image extent
        x1, y1 = maps.default_x1, maps.default_y1
        x2, y2 = maps.default_x2, maps.default_y2

    bbox = mapnik.Envelope(mapnik.Coord(x1,y1), mapnik.Coord(x2,y2))
    m.zoom_to_box(bbox)
    # Render image and send out the response
    mapnik.render(m, draw)
    img = draw.tostring('png')
    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png' 
    response.write(img)

    # if testing via django unit tests, close out the connection
    if DB_NAME != settings.DATABASE_NAME:
        del m

    return response
