from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.db import connection
from lingcod.common import mimetypes, utils

import settings

from lingcod.staticmap.models import *

def show(request, map_name='default'):
    """Display a map with the study region geometry.  """
    maps = get_object_or_404(MapConfig,mapname=map_name)
    mapfile = str(maps.mapfile.path)
     
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
    # construct filter and replace the MPA_FILTER tag
    try:
        mpas = str(request.REQUEST['mpas']).split(',')
        # make sure all given mpas are integers
        mpas = [int(x) for x in mpas if x.isdigit()]
        mpa_queries = ['[id] = %d' % x for x in mpas] 
        xmltext = xmltext.replace("MPA_FILTER", " or ".join(mpa_queries))
    except KeyError:
        # If MPAs are not specified, don't render ANY of them
        xmltext = xmltext.replace("MPA_FILTER",'')

    # Assume MEDIA_ROOT and DATABASE_NAME are always defined
    xmltext = xmltext.replace("MEDIA_ROOT",settings.MEDIA_ROOT)
    xmltext = xmltext.replace("GEOMETRY_DB_SRID",str(settings.GEOMETRY_DB_SRID))

    # Replace table names for mpas and mpaarrays
    mpa_class = utils.get_mpa_class()
    xmltext = xmltext.replace("MM_MPA", str(mpa_class._meta.db_table))

    conn = connection.settings_dict
    connection_string = ""
    connection_string += "<Parameter name='dbname'>%s</Parameter>" % conn['DATABASE_NAME']
    connection_string += "<Parameter name='user'>%s</Parameter>" % conn['DATABASE_USER']
    connection_string += "<Parameter name='password'>%s</Parameter>" % conn['DATABASE_PASSWORD']
    connection_string += "<Parameter name='host'>%s</Parameter>" % conn['DATABASE_HOST']
    # if testing via django unit tests, close out the connection
    if conn['DATABASE_NAME'] != settings.DATABASE_NAME:
        connection_string += "<Parameter name='persist_connection'>false</Parameter>"

    xmltext = xmltext.replace("DATABASE_CONNECTION",connection_string)
    mapnik.load_map_from_string(m,xmltext)

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
    if conn['DATABASE_NAME'] != settings.DATABASE_NAME:
        del m

    return response
