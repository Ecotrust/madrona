from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseServerError, HttpResponseForbidden
from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from lingcod.common import mimetypes

from lingcod.manipulators.manipulators import *

from django.contrib.gis.geos import GEOSGeometry, Polygon, Point, LinearRing
from lingcod.studyregion.models import StudyRegion
from lingcod.common.utils import KmlWrap
from django.conf import settings


def multi_generic_manipulator_view(request, manipulators):

    # conversion jiggery-pokery to get the QueryDict into appropriate kwarg format
    kwargs = {}
    for key,val in request.POST.items():
        kwargs[str(key)] = str(val)
                
    # parse out which manipulators are requested
    manipulator_list = manipulators.split(',')

    # run the manipulators in order presented
    for manipulator in manipulator_list:

        # try to bind the incoming manipulator string to an existing class
        try:
            manipClass = eval( manipulator + 'Manipulator' )
        except NameError:
            return HttpResponse( "Manipulator " + manipulator + " does not exist." )

        # 'get' requests assume the intent is to get a related parameter-entry form
        if request.method == 'GET':
            if manipClass.Form.available:
                form = manipClass.Form()
                return render_to_response( 'common/base_form.html', RequestContext(request,{'form': form}))
            else: # this manipulator has no form, just error out
                return HttpResponse( "Manipulator " + manipulator + " does not support GET requests." )
                
        else: # post request: run this manipulator
            if manipClass.Form.available: # validate a related form, if such exists
                form = manipClass.Form( kwargs )
                if form.is_valid():
                
                    new_shape = form.manipulated_geometry
                    
                    # put the resulting shape back into the kwargs as the target_shape
                    kwargs['target_shape'] = new_shape.wkt
                     
                else: # invalid parameters - bounce form back to user
                    return render_to_response( 'common/base_form.html', RequestContext(request,{'form': form}))
                    
            else: # no form exists - run this manipulator directly, passing the POST params directly as kwargs
                
                manip_inst = manipClass( **kwargs )
                new_shape = manip_inst.manipulate()
                
                # put the resulting shape back into the kwargs as the target_shape
                kwargs['target_shape'] = new_shape.wkt
                  
                
    # manipulators ran fine and the resulting shape is ready for outbound processing
    new_shape.transform(settings.GEOMETRY_DB_SRID)
    new_shape = new_shape.simplify(20, preserve_topology=True)
    new_shape.transform(4326)
              
    result = '<Document><Placemark><Style><LineStyle> <color>ffffffff</color> <width>2</width></LineStyle><PolyStyle> <color>80ffffff</color> </PolyStyle></Style>'+new_shape.kml+'</Placemark></Document>'
                
    #return HttpResponse(result, content_type = 'text/plain')
    
    return render_to_response( 'studyregion/studyregion.html', RequestContext(request,{'extra_kml': result, 'api_key':settings.GOOGLE_API_KEY}))
    

    
    
def testView( request ):
    trans_geom = StudyRegion.objects.all()[0].geometry 
    trans_geom.transform(4326)
        
    w = trans_geom.extent[0]
    s = trans_geom.extent[1]
    e = trans_geom.extent[2]
    n = trans_geom.extent[3]
    
    center_lat = trans_geom.centroid.y 
    center_lon = trans_geom.centroid.x
            
    target_shape = Polygon( LinearRing([ Point( center_lon, center_lat ), Point( e, center_lat ), Point( e, s ), Point( center_lon, s ), Point( center_lon, center_lat)]))
    
    new_req = HttpRequest()
    new_req.method = 'POST'
    new_req.POST.update({'target_shape':target_shape.wkt, "n":"40", "s":"20", "e":"-117", "w":"-118"})
    response = multi_generic_manipulator_view( new_req, 'ClipToStudyRegion,ClipToGraticules' )
    return response
    
    
    