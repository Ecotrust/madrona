from django.template import RequestContext, loader, Context , Template
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.template.loader import get_template
from lingcod.spacing.models import *
from django.template.defaultfilters import slugify
import lingcod.intersection.views as int_views
import xlwt

def Index(request):
    return render_to_response('map.html', RequestContext(request))

def LandKML(request):
    land = Land.objects.all()
    response = HttpResponse(kml_doc_from_queryset(land), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'land'
    return response
    
def SpacingPointKML(request):
    sp_points = SpacingPoint.objects.all()
    response = HttpResponse(kml_doc_from_queryset(sp_points), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'SpacingPoints'
    return response
    
def SpacingNetworkKML(request):
    sp_graph = PickledGraph.objects.all()[0].graph
    geometries = points_from_graph(sp_graph)
    geometries.extend(lines_from_graph(sp_graph))
    [ g.transform(settings.GEOMETRY_CLIENT_SRID) for g in geometries ]
    response = HttpResponse(kml_doc_from_geometry_list(geometries), mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'SpacingPoints'
    return response

def FishDistanceKML(request):
    lat1 = float(request.GET.get('lat1'))
    lon1 = float(request.GET.get('lon1'))
    lat2 = float(request.GET.get('lat2'))
    lon2 = float(request.GET.get('lon2'))
    pnt1 = geos.GEOSGeometry( geos.Point(lon1,lat1), srid=4326 )
    pnt1.transform(3310)
    pnt2 = geos.GEOSGeometry( geos.Point(lon2,lat2), srid=4326 )
    pnt2.transform(3310)
    distance, line = fish_distance(pnt1,pnt2)
    line.srid = 3310
    line.transform(4326)
    response = HttpResponse('<Placemark>' + line.kml + '</Placemark>', mimetype='application/vnd.google-earth.kml+xml')
    response['Content-Disposition'] = 'attachment; filename="%s.kml"' % 'line'
    return response
    
def create_pickled_graph_from_all_land(request):
    if request.user.is_staff:
        create_pickled_graph()
        return HttpResponseRedirect('/admin/spacing/pickledgraph/')
    else:
        return HttpResponseForbidden
    
def spacing_workbook(in_dict, ws_title):
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('spacing_matrix')
    ws = spacing_worksheet(in_dict, ws_title,ws)
    return wb
    
def spacing_worksheet(in_dict,ws_title,ws):
    results = distance_matrix_and_labels(in_dict, straight_line=False)
    straight_results = distance_matrix_and_labels(in_dict, straight_line=True)
    title1 = "Shortest Distance Without Crossing Land From Edges"
    title2 = "Straight Line Distance From Edges"
    results_dict = { title1 : results, title2 : straight_results }
    current_row = 0
    # put the title at the top
    if ws_title is not None:
        ws.row(current_row).write(0,unicode(ws_title))
        current_row += 2
        
    for title, results in results_dict.items():
        ws.row(current_row).write(0,title)
        current_row += 1
        label_list = results['labels']
        dist_mat = results['matrix']
        # write the header labels row across the top
        for i,lab in enumerate(label_list):
            ws.row(current_row).write(i+1,unicode(lab) )
        current_row += 1
    
        # write the rest of the matrix
        for i,row in enumerate(dist_mat):
            # write the label in the first column
            ws.row(current_row).write(0,unicode(label_list[i]))
            # write the distance values
            for x,distance in enumerate(row):
                ws.row(current_row).write(x+1,distance['distance'])
            current_row += 1
        current_row += 1
    return ws