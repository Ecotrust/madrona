from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from lingcod.intersection.models import *
from lingcod.intersection.forms import *
from django.utils.simplejson import dumps as json_encode
import xlwt
import csv

def split_to_single_shapefiles(request, mfshp_pk):
    if request.user.is_staff:
        if request.method == 'POST':
            form = SplitToSingleFeaturesForm(mfshp_pk, request.POST)
            if form.is_valid():
                mfshp_pk = form.cleaned_data['mfshp_pk']
                shp_field = form.cleaned_data['shp_field']
                mfshp = MultiFeatureShapefile.objects.get(pk=mfshp_pk)
                mfshp.split_to_single_feature_shapefiles(str(shp_field))
                return HttpResponseRedirect('/admin/intersection/singlefeatureshapefile/')
        else:
            form = SplitToSingleFeaturesForm(mfshp_pk)
    else:
        return HttpResponseForbidden
    
    c = csrf(request)
    c.update({'form': form, 'mfshp_pk_key': mfshp_pk}, current_app='intersection.admin')
    return render_to_response('split_to_single_feature_shapefiles.html', c)

def test_drawing_intersect(request):
    if request.method == 'POST':
        form = TestIntersectionForm(request.POST)
        if form.is_valid():
            geom = geos.fromstr(form.cleaned_data['geometry'])
            org_scheme = form.cleaned_data['org_scheme']
            format = form.cleaned_data['format']
            geom.transform(3310)
            if org_scheme == 'None':
                result = intersect_the_features(geom)
                if format=='html':
                    return render_to_response('generic_results.html', {'result': use_sort_as_key(result)})
                elif format=='csv':
                    return build_csv_response(result, str(hash(geom)) )
                elif format=='json':
                    return HttpResponse(json_encode(result), mimetype='text/json')
            else:
                osc = OrganizationScheme.objects.get(pk=org_scheme)
                result = osc.transformed_results(geom)
                if format=='html':
                    return render_to_response('transformed_results.html', {'result': use_sort_as_key(result)})
                elif format=='csv':
                    return build_csv_response(result, str(hash(geom)) )
                elif format=='json':
                    return HttpResponse(json_encode(result), mimetype='text/json')
    else:
        form = TestIntersectionForm()
    return render_to_response('polygon_form.html', {'form': form})

def build_csv_response(results, file_name, leave_out=['feature_map_id','org_scheme_id']):
    response = HttpResponse(mimetype='application/csv')
    response['Content-Disposition'] = 'attachement; filename=%s.csv' % ( file_name )
    writer = csv.writer(response)
    if results.__class__.__name__<>'list':
        results = [results]
    header_row = ['Habitat']
    header_row.extend( [ k.replace('_',' ').title() for k in results[0][ results[0].keys()[0] ].keys() ] )
    header_row = remove_elements(header_row,[lo.replace('_',' ').title() for lo in leave_out] )
    row_matrix = [header_row]
        
    for result in results:
        for hab,sub_dict in result.iteritems():
            new_row = [hab]
            wanted_values = []
            for k,v in sub_dict.iteritems():
                if k not in leave_out:
                    wanted_values.append(v)
            new_row.extend(wanted_values)
            row_matrix.append(new_row)
    
    for row in row_matrix:
        writer.writerow(row)
        
    return response
    
def build_excel_response(file_name, workbook):
    """
    This method assumes you've built an excel workbook elsewhere and just want to build a response object from it.
    """
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachement; filename=%s.xls' % ( file_name )
    workbook.save(response)

    return response
    
def build_array_mpa_csv_response(results, file_name, feature_name, feature_type='MPA', leave_out=['feature_map_id','org_scheme_id']):
    response = HttpResponse(mimetype='application/csv')
    response['Content-Disposition'] = 'attachement; filename=%s.csv' % ( file_name )
    writer = csv.writer(response)
    if results.__class__.__name__<>'list':
        results = [results]
    if feature_type.lower()=='mpa':
        feature_type = 'MPA'
    else:
        feature_type = feature_type.title()
    header_row = [feature_type,'Habitat']
    header_row.extend( [ k.replace('_',' ').title() for k in results[0][ results[0].keys()[0] ].keys() ] )
    header_row = remove_elements(header_row,[lo.replace('_',' ').title() for lo in leave_out] )
    row_matrix = [header_row]

    for result in results:
        for hab,sub_dict in result.iteritems():
            new_row = [feature_name,hab]
            wanted_values = []
            for k,v in sub_dict.iteritems():
                if k not in leave_out:
                    wanted_values.append(v)
            new_row.extend(wanted_values)
            row_matrix.append(new_row)

    for row in row_matrix:
        writer.writerow(row)

    return response
    
def remove_elements(the_list,remove_list):
    for r in remove_list:
        try:
            the_list.remove(r)
        except ValueError:
            continue
    return the_list
        
def test_poly_intersect(request):
    if request.method == 'POST':
        form = TestPolygonIntersectionForm(request.POST)
        if form.is_valid():
            geom = geos.fromstr(form.cleaned_data['geometry'])
            org_scheme = form.cleaned_data['org_scheme']
            format = form.cleaned_data['format']
            geom.transform(3310)
            if org_scheme == 'None':
                result = intersect_the_features(geom)
                if format=='html':
                    return render_to_response('generic_results.html', {'result': result})
                elif format=='csv':
                    return build_csv_response(result, str(hash(geom)) )
                elif format=='json':
                    return HttpResponse(json_encode(result), mimetype='text/json')
            else:
                osc = OrganizationScheme.objects.get(pk=org_scheme)
                result = osc.transformed_results(geom)
                if format=='html':
                    return render_to_response('transformed_results.html', {'result': use_sort_as_key(result)})
                elif format=='csv':
                    return build_csv_response(result, str(hash(geom)) )
                elif format=='json':
                    return HttpResponse(json_encode(result), mimetype='text/json')
    else:
        form = TestPolygonIntersectionForm()
    return render_to_response('testpolygon_intersection.html', {'form': form})

def default_intersection(request, format, geom_wkt):
    geom = geos.fromstr(geom_wkt)
    geom.transform(3310)
    result = intersect_the_features(geom)
    if format=='html':
        return render_to_response('generic_results.html', {'result': result})
    elif format=='csv':
        return build_csv_response(result, str(hash(geom)) )
        
def organized_intersection(request, org_scheme, format, geom_wkt):
    geom = geos.fromstr(geom_wkt)
    geom.transform(3310)
    osc = OrganizationScheme.objects.get(pk=int(org_scheme) )
    result = osc.transformed_results(geom)
    if format=='html':
        return render_to_response('transformed_results.html', {'result': use_sort_as_key(result)})
    elif format=='csv':
        return build_csv_response(result, str(hash(geom)) )
    elif format=='json':
        return HttpResponse(json_encode(result), mimetype='text/json')
        
def organized_intersection_by_name(request, org_scheme_name, format, geom_wkt):
    org_scheme_pk = OrganizationScheme.objects.get(name=org_scheme_name).pk
    return organized_intersection(request, org_scheme_pk, format, geom_wkt)

def org_scheme_info(request, org_id):
    osc = OrganizationScheme.objects.get(pk=org_id)
    subdict = osc.info
    return HttpResponse(json_encode(subdict), mimetype='text/json')
    
def org_scheme_pk_from_name(request, name):
    osc_pk = OrganizationScheme.objects.get(name=name).pk
    result = {'pk': osc_pk}
    return HttpResponse(json_encode(result), mimetype='text/json')

def all_org_scheme_info(request):
    oscs = OrganizationScheme.objects.all()
    dict = {}
    for osc in oscs:
        subdict = osc.info
        dict[str(osc.pk)] = subdict
    return HttpResponse(json_encode(dict), mimetype='text/json')
    
#def test_poly_intersect_csv(request, type):
#    if request.method == 'POST':
#        form = TestPolygonIntersectionForm(request.POST)
#        if form.is_valid():
#            geom = geos.fromstr(form.cleaned_data['geometry'])
#            org_scheme = form.cleaned_data['org_scheme']
#            geom.transform(3310)
#            if org_scheme == 'None':
#                result = intersect_the_features(geom)
#                if type=='html':
#                   return render_to_response('generic_results.html', {'result': result}) 
#            else:
#                osc = OrganizationScheme.objects.get(pk=org_scheme)
#                result = osc.transformed_results(geom)
#                if type=='html':
#                    return render_to_response('transformed_results.html', {'result': result})
#                
#            return build_csv_response(result, str(hash(geom)) )
#    else:
#        form = TestPolygonIntersectionForm()
#    return render_to_response('testpolygon_intersection.html', {'form': form})
