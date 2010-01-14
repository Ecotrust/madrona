from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes
from lingcod.common.utils import KmlWrap, LargestPolyFromMulti
import lingcod.intersection.models as int_models
import lingcod.intersection.views as int_views
import mlpa.models as mlpa
from django.template.defaultfilters import slugify

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