from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti
import lingcod.intersection.models as int_models
import lingcod.intersection.views as int_views
import mlpa.models as mlpa
from django.template.defaultfilters import slugify
#import django.contrib.gis.geos

from django.conf import settings
from django.utils.simplejson import dumps as json_encode


def mpa_habitat_representation(request, mpa_id, format='json', with_geometries=False, with_kml=False):
    mpa = mlpa.MlpaMpa.objects.get(pk=mpa_id)
    geom = mpa.geometry_final
    if mpa.is_estuary is None:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
    elif mpa.is_estuary:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE)
    else:
        org_sch = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
        
    result = org_sch.transformed_results(geom,with_geometries,with_kml)
    if format=='csv':
        return int_views.build_csv_response(result, slugify(mpa.name) )
    elif format=='json':
        return HttpResponse(json_encode(result), mimetype='text/json')
    # I was going to try and make this interface with the intersection app through urls so that
    # the intersection app could be on a different server but that's not working out and I'm in 
    # a hurry.
    # redirect_url = '/intersection/%s/%s/%s/' % (org_scheme_name,format,str(geom_wkt))
    # return HttpResponseRedirect(redirect_url)

def oc_or_est(results,oc_keys,est_keys):
    """
    labels each result as from estuaries, open coast, or combined
    """
    for hab,sub_dict in results.iteritems():
        if hab in oc_keys and hab in est_keys:
            sub_dict.update({'from':'Combined'})
        elif hab in oc_keys:
            sub_dict.update({'from':'Open Coast'})
        else:
            sub_dict.update({'from':'Estuarine'})
    return results

def oc_or_est_from_org_scheme(results):
    for hab,sub_dict in results.iteritems():
        for k,v in sub_dict.iteritems():
            if k == 'org_scheme_id':
                if v==int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE).pk:
                    new_part = {'from':'Estuaries'}
                elif v==int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST).pk:
                    new_part = {'from':'Open Coast'}
        sub_dict.update(new_part)
    return results

def geometries_to_wkt(results,srid=None, simplify=None):
    """
    Take a dictionary, find values that are geometry objects and replace them with wkt representations of the geometries.
    """
    geometry_classes = ['GeometryCollection','MultiPolygon','Polygon','MultiLineString','LineString','MultiPoint','Point']
    for k,v in results.iteritems():
        if v.__class__.__name__ in geometry_classes:
            new_geom = v
            if simplify:
                print str(v.num_points) + ': ',
                v = v.simplify(simplify,True)
                print str(v.num_points)
            if srid:
                v.set_srid(settings.GEOMETRY_DB_SRID)
                v.transform(srid)
            results[k] = v.wkt
        elif v.__class__.__name__=='dict':
            v.update(geometries_to_wkt(v,srid,simplify))
    return results
    
def array_habitat_replication(request, array_id, format='json'):
    array = mlpa.MpaArray.objects.get(pk=array_id)
    if format=='json':
        template = 'array_replication_page.html'
    elif format=='print':
        template = 'array_replication_page_print.html'
    return render_to_response(template, {'results': array.clusters_with_habitat, 'array': array}, context_instance=RequestContext(request) )
            
def array_habitat_representation_summed(request, array_id, format='json', with_geometries=False, with_kml=False, oc_est_combined=False):
    if format != 'json':
        with_geometries = False
        with_kml = False
    array = mlpa.MpaArray.objects.get(pk=array_id)
    oc_gc = array.opencoast_geometry_collection
    est_gc = array.estuarine_geometry_collection
    oc_org = int_models.OrganizationScheme.objects.get(name=settings.SAT_OPEN_COAST)
    est_org = int_models.OrganizationScheme.objects.get(name=settings.SAT_ESTUARINE)
    oc_results = oc_org.transformed_results(oc_gc,with_geometries,with_kml)
    est_results = est_org.transformed_results(est_gc,with_geometries,with_kml)
    oc_keys = oc_results.keys()
    est_keys = est_results.keys()
    if oc_est_combined:
        all_results = [oc_results,est_results]
        results = int_models.sum_results(all_results)
        results = oc_or_est(results,oc_keys,est_keys)
        results = geometries_to_wkt(results)
    elif not oc_est_combined and format=='json':
        oc_results = geometries_to_wkt(oc_results)
        est_results = geometries_to_wkt(est_results)
        results = { settings.SAT_OPEN_COAST: oc_results, settings.SAT_ESTUARINE: est_results }
    elif not oc_est_combined and format=='csv':
        return int_views.build_csv_response([oc_or_est_from_org_scheme(oc_results), oc_or_est_from_org_scheme(est_results)], slugify(array.name) )
        
    if format=='json':
        return HttpResponse(json_encode(results), mimetype='text/json')
    elif format=='csv':
        return int_views.build_csv_response(results, slugify(array.name) )
    