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
     
    try:
        width = int(request.REQUEST['width'])
        height = int(request.REQUEST['height'])
    except:
        # fall back on defaults
        width, height = 800, 600

    try:
        x1, y1, x2, y2 = split(str(request.REQUEST['bbox']), ',')
    except:
        # fall back on default image extent
        x1, y1, x2, y2 = -121.2, 31.2, -116.6, 35 # so cal
        # x1, y1, x2, y2 = -180,-90,180,90 # whole world 

    import mapnik
    draw = mapnik.Image(width,height)
    m = mapnik.Map(width,height)
    mapnik.load_map(m, mapfile)
    bbox = mapnik.Envelope(mapnik.Coord(x1,y1), mapnik.Coord(x2,y2))
    m.zoom_to_box(bbox)
    mapnik.render(m, draw)
    img = draw.tostring('png')
    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png' 
    response.write(img)
    return response
