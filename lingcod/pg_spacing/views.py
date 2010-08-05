from django.template import RequestContext, loader, Context , Template
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template
from lingcod.pg_spacing.models import *

def Index(request):
    return render_to_response('pg_spacing/map.html', RequestContext(request))

def LandKML(request):
    land = Land.objects.all()
    response = HttpResponse(kml_doc_from_queryset(land), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'land'
    return response

def FishDistanceKML(request):
    lat1 = float(request.GET.get('lat1'))
    lon1 = float(request.GET.get('lon1'))
    lat2 = float(request.GET.get('lat2'))
    lon2 = float(request.GET.get('lon2'))
    pnt1 = geos.GEOSGeometry( geos.Point(lon1,lat1), srid=4326 )
    pnt1.transform(settings.GEOMETRY_DB_SRID)
    pnt2 = geos.GEOSGeometry( geos.Point(lon2,lat2), srid=4326 )
    pnt2.transform(settings.GEOMETRY_DB_SRID)
    distance, line = fish_distance(pnt1,pnt2)
    line.srid = settings.GEOMETRY_DB_SRID
    line.transform(4326)
    response = HttpResponse('<Placemark>' + line.kml + '</Placemark>', mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'line'
    return response# Create your views here.
