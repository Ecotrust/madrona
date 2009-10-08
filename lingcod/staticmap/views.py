from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

from lingcod.staticmap.models import *

def staticmap(request):
    """Display a map with the study region geometry.
    """
    import mapnik
    draw = mapnik.Image(800,600)
    mapfile = '../../media/staticmap/world_styles.xml'
    m = mapnik.Map(800,600)
    mapnik.load_map(m, mapfile)
    #bbox = mapnik.Envelope(mapnik.Coord(-180, -90), mapnik.Coord(180,90))
    bbox = mapnik.Envelope(mapnik.Coord(-121.2, 31.2), mapnik.Coord(-116.6, 35))
    m.zoom_to_box(bbox)
    mapnik.render(m, draw)
    img = draw.tostring('png')
    response = HttpResponse()
    response['Content-length'] = len(img)
    response['Content-Type'] = 'image/png' 
    response.write(img)
    return response


