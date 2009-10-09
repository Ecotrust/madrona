from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

from lingcod.staticmap.models import *

def show(request, map_name):
    """Display a map with the study region geometry.
    """
    maps = get_object_or_404(MapConfig,mapname=map_name)
    mapfile = str(maps.mapfile)
     
    # Grab the image dimensions
    try:
        width = int(request.REQUEST['width'])
        height = int(request.REQUEST['height'])
    except:
        # fall back on defaults
        width, height = maps.default_width, maps.default_height

    # Create a blank image and load the mapfile
    import mapnik
    draw = mapnik.Image(width,height)
    m = mapnik.Map(width,height)
    mapnik.load_map(m, mapfile)

    # Grab the bounding coordinates and set them if specified
    try:
        x1, y1, x2, y2 = split(str(request.REQUEST['bbox']), ',')
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
    return response
