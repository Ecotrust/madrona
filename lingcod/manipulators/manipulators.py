from django.contrib.gis.geos import GEOSGeometry, Polygon, Point, LinearRing
from django import forms
from lingcod.studyregion.models import *
from django.conf import settings
from lingcod.common.utils import LargestPolyFromMulti
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
# manipulatorsDict is bound to this module (won't be reinitialized if module is imported twice)
manipulatorsDict = {}


class BaseManipulator(object):
    '''
        BaseManipulator should be used as the parent class to all manipulator classes.
        The manipulate() function should be overridden with suitable definition, it is this function that will
            be called automatically when your manipulator class is included in the Mpa.Options.manipulators list.
            This function generally takes as input a target shape geometry, and should return a call to result() 
            containing the 'clipped_shape' and optionally a rendered template 'html' and 'success' value.
            'clipped_shape' is the new shape as a result of the manipulator
            'html' is generally a template that might be displayed by the client
            'success' is a signal, '1' or '0', as to whether the manipulation succeeded or not
        The do_template() function can be used to render a template with appropriate context
        The target_to_valid_geom() function can be used to generate a geometry from target shape
        The result() function should be used for the manipulator return value to ensure that all necessary
            key/value pairs are provided.
        Three useful exceptions are provided as well:
            InternalException is used for exceptions or errors that are considered 'server-side' 
                or 'out of the users control', such as failed database access, or failed geometry operation.
            InvalidGeometryException is used for exceptions or errors resulting from an innapropriate mpa geometry 
                such as a point, line, or otherwise invalid geometry.
            HaltManipulations is used for errors, not already handled by InternalException or InvalidGeometryException,
                that should prevent any further manipulations from taking place. This could be useful in cases such as
                when an mpa geometry is outside of the study region. In such cases there is no need for further 
                manipulations as such an mpa entry is already deemed inappropriate for our use.
    '''
    def __init__(self, **kwargs):
        self.kwargs = kwargs
     
    def manipulate(self):
        raise NotImplementedError()
        
    def do_template(self, key, internal_message='', extra_context={}):
        context = {'MEDIA_URL':settings.MEDIA_URL, 'INTERNAL_MESSAGE': internal_message}
        context.update(extra_context)
        return render_to_string(self.Options.html_templates[key], context)
  
    def target_to_valid_geom(self, shape):
        try:
            target = GEOSGeometry(shape)     
        except Exception, e:
            raise self.InvalidGeometryException(e.message)
        if not target.valid:
            raise self.InvalidGeometryException()
        target.set_srid(settings.GEOMETRY_CLIENT_SRID) 
        return target
  
    def result(self, clipped_shape, html="", success="1"):
        return {"clipped_shape": clipped_shape, "html": html, "success": success}
    
    class Form:
        available = False
        
    class Options:
        name = 'Manipulator base class'
        template_name = 'manipulators/manipulator_default.html'
        html_templates = {
            'invalid_geom':'manipulators/invalid_geometry.html',
            'internal':'manipulators/internal_error.html',
            'unexpected':'manipulators/unexpected_error.html'
        }
    
    class InternalException(Exception):
        def __init__(self, message="", status_html=None, success="0"):
            self.message = message
            if status_html == None:
                self.template = BaseManipulator.do_template(BaseManipulator(), 'internal', message)
                self.html = self.template
            else:
                self.html = status_html
            self.success = success
        def __str__(self):
            return repr(self.message)
    
    class InvalidGeometryException(Exception):
        def __init__(self, message="", status_html=None, success="0"):
            self.message = message
            if status_html == None:
                self.template = BaseManipulator.do_template(BaseManipulator(), 'invalid_geom', message)
                self.html = self.template
            else:
                self.html = status_html
            self.success = success
        def __str__(self):
            return repr(self.message)   
    
    class HaltManipulations(Exception):
        def __init__(self, message="", status_html="", success="0"):
            self.message = message
            self.html = status_html
            self.success = success
        def __str__(self):
            return repr(self.message)
           
class ClipToShapeManipulator(BaseManipulator):
    '''
        required arguments:
            target_shape: GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
            clip_against: GEOSGeometry of the shape to clip against, in srid GEOMETRY_CLIENT_SRID (4326)
        concerning **kwargs:
            kwargs is included to prevent errors resulting from extra arguments being passed to this manipulator from the generic view
        manipulate() return value:
            a call to self.result() 
            with required parameter 'clipped_shape': 
                The returned shape geometry should be in srid GEOMETRY_CLIENT_SRID (4326) 
                The clipped shape will be the largest (in area) polygon result from intersecting 'target_shape' with 'clip_against' 
            and optional parameters 'html' and 'success':
                The html is usually a template that will be displayed to the client, explaining the manipulation
                if not provided, this will remain empty
                The success parameter is defined as '1' for success and '0' for failure
                if not provided, the default value, '1', is used

        html_templates=='internal'   
                            This represents an 'internal error' and is accessed by raising a ManipulatorInternalException
                            This should occur under the following circumstances:
                                if geometry can not be generated from "clip_against" 
                                or intersection call failed
                            clipped_shape will be returned as None
        html_templates=='invalid_geom'   
                            This represents an 'user error' and is accessed by raising an InvalidGeometryException
                            This should occur under the following circumstances:
                                if geometry can not be generated from "target_shape" 
                                or if "target_shape" is not a valid geometry
                            clipped_shape will be returned as None         
        html_templates==2   clipped shape is empty (no overlap with "clip_against")
        html_templates==0   if "target_shape" is successfully clipped to "clip_against"
    '''
 
    def __init__(self, target_shape, clip_against=None, **kwargs):
        self.target_shape = target_shape
        self.clip_against = clip_against
    
    def manipulate(self):
        #extract target_shape geometry
        target_shape = self.target_to_valid_geom(self.target_shape)

        #extract clip_against geometry
        try:
            clip_against = GEOSGeometry(self.clip_against)
            clip_against.set_srid(settings.GEOMETRY_CLIENT_SRID)
        except Exception, e:
            raise self.InternalException("Exception raised in ClipToShapeManipulator while initializing geometry on self.clip_against: " + e.message)
        
        if not clip_against.valid:
            raise self.InternalException("ClipToShapeManipulator: 'clip_against' is not a valid geometry")
        
        #intersect the two geometries
        try:
            clipped_shape = target_shape.intersection( clip_against )
        except Exception, e:
            raise self.InternalException("Exception raised in ClipToShapeManipulator while intersecting geometries: " + e.message)  
        
        #if there was no overlap (intersection was empty)
        if clipped_shape.area == 0:
            status_html = self.do_template("2")
            #message = "intersection resulted in empty geometry"
            #return self.result(clipped_shape, target_shape, status_html, message)
            return self.result(clipped_shape, status_html)
         
        #if there was overlap
        largest_poly = LargestPolyFromMulti(clipped_shape)
        status_html = self.do_template("0")
        #message = "'target_shape' was clipped successfully to 'clip_against'"
        #return self.result(largest_poly, target_shape, status_html, message)
        return self.result(largest_poly, status_html)
    '''
    #the following is USED FOR TESTING, 
    #assigns db current studyregion as the shape to clip against
    class Form(forms.Form):
        available = True
        target_shape = forms.CharField( widget=forms.HiddenInput )
        clip_against = forms.CharField( widget=forms.HiddenInput, required=False )
        
        def clean(self):
            data = self.cleaned_data
            
            #used for sandbox testing
            clippy = StudyRegion.objects.current().geometry
            clippy.transform(settings.GEOMETRY_CLIENT_SRID)
            data["clip_against"] = clippy.wkt 
            
            #my_manipulator = ClipToShapeManipulator( **kwargs )
            my_manipulator = ClipToShapeManipulator( data['target_shape'], data['clip_against'] )
            self.manipulation = my_manipulator.manipulate()
            return self.cleaned_data
    '''
    class Options:
        name = 'ClipToShape'
        html_templates = {
            '0':'manipulators/shape_clip.html', 
            '2':'manipulators/outside_shape.html', 
        }

manipulatorsDict[ClipToShapeManipulator.Options.name] = ClipToShapeManipulator

        
        
class ClipToStudyRegionManipulator(BaseManipulator):
    '''
        required argument: 
            target_shape: GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional argument:
            generally USED FOR TESTING ONLY
            study_region: GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        concerning **kwargs:
            kwargs is included to prevent errors resulting from extra arguments being passed to this manipulator from the generic view
        manipulate() return value:
            a call to self.result() 
            with required parameter 'clipped_shape': 
                The returned shape geometry should be in srid GEOMETRY_CLIENT_SRID (4326) 
                The clipped shape will be the largest (in area) polygon result from intersecting target_shape with the study region 
            and optional parameters 'html' and 'success':
                The html is usually a template that will be displayed to the client, explaining the manipulation
                if not provided, this will remain empty
                The success parameter is defined as '1' for success and '0' for failure
                if not provided, the default value, '1', is used
            
        html_templates=='internal'   
                            This represents an 'internal error' and is accessed by raising a ManipulatorInternalException
                            This should occur under the following circumstances:
                                if Study Region not found in database
                                or intersection call failed
                            clipped_shape will be returned as None
        html_templates=='invalid_geom'   
                            This represents an 'user error' and is accessed by raising a InvalidGeometryException
                            This should occur under the following circumstances:
                                if geometry can not be generated from target_shape 
                                or if target_shape is not a valid geometry
                            clipped_shape will be returned as None         
        html_templates==2   clipped shape is empty (no overlap with Study Region)
        html_templates==0   if target_shape is successfully clipped to Study Region
    '''  
     
    def __init__(self, target_shape, study_region=None, **kwargs):
        self.target_shape = target_shape
        self.study_region = study_region
        
    def manipulate(self):
        #extract target_shape geometry
        target_shape = self.target_to_valid_geom(self.target_shape)

        #extract study_region geometry
        #study_region argument is FOR UNIT-TESTING PURPOSES ONLY, otherwise we access the database
        if self.study_region is not None:
            try:
                study_region = GEOSGeometry(self.study_region)
                study_region.set_srid(settings.GEOMETRY_CLIENT_SRID)
                study_region.transform(settings.GEOMETRY_DB_SRID)
            except Exception, e:
                raise self.InternalException("Exception raised in ClipToStudyRegionManipulator while initializing study region geometry: " + e.message)
        else:
            try:
                study_region = StudyRegion.objects.current().geometry
            except Exception, e:
                raise self.InternalException("Exception raised in ClipToStudyRegionManipulator while obtaining study region geometry from database: " + e.message)    
        
        #intersect the two geometries
        try:
            target_shape.transform(settings.GEOMETRY_DB_SRID)
            clipped_shape = target_shape.intersection(study_region)
            target_shape.transform(settings.GEOMETRY_CLIENT_SRID)
            clipped_shape.transform(settings.GEOMETRY_CLIENT_SRID)
        except Exception, e:
            raise self.InternalException("Exception raised in ClipToStudyRegionManipulator while intersecting geometries: " + e.message)  
        
        #if there was no overlap (intersection was empty)
        if clipped_shape.area == 0:
            message = "clipped geometry is empty (there was no intersection/overlap with study region)"
            status_html = self.do_template("2")
            raise self.HaltManipulations(message, status_html)
            
        #if there was overlap
        largest_poly = LargestPolyFromMulti(clipped_shape)
        #message = "target_shape was clipped to study region"
        status_html = self.do_template("0")
        #return self.result(largest_poly, target_shape, status_html, message)
        return self.result(largest_poly, status_html)
        
        
    class Options:
        name = 'ClipToStudyRegion'
        html_templates = {
            '0':'manipulators/studyregion_clip.html', 
            '2':'manipulators/outside_studyregion.html', 
        }
        
      
manipulatorsDict[ClipToStudyRegionManipulator.Options.name] = ClipToStudyRegionManipulator
    
    
class ClipToGraticuleManipulator(BaseManipulator):
    '''
        required argument: 
            target_shape:  GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
        optional arguments:
            north, south, east, west:  expressed in srid GEOMETRY_CLIENT_SRID (4326) 
        concerning **kwargs:
            kwargs is included to prevent errors resulting from extra arguments being passed to this manipulator from the generic view
        manipulate() return value:
            a call to self.result() 
            with required parameter 'clipped_shape': 
                The returned shape geometry should be in srid GEOMETRY_CLIENT_SRID (4326) 
                The clipped shape will be the largest (in area) polygon result from clipping target_shape with the requested graticule(s) 
            and optional parameters 'html' and 'success':
                The html is usually a template that will be displayed to the client, explaining the manipulation
                if not provided, this will remain empty
                The success parameter is defined as '1' for success and '0' for failure
                if not provided, the default value, '1', is used
            
        html_templates=='invalid'   
                            This represents an 'internal error' and is accessed by raising a ManipulatorInternalException
                            This should occur under the following circumstances:
                                if polygon could not be created from graticules
                                or intersection call failed
                            clipped_shape will be returned as None
        html_templates=='invalid_geom'   
                            This represents an 'user error' and is accessed by raising a InvalidGeometryException
                            This should occur under the following circumstances:
                                if geometry can not be generated from target_shape 
                                or target_shape is not valid geometry
                            clipped_shape will be returned as None
        html_templates==2   if the clipped geometry is empty
        html_templates==0   if target_shape is successfully clipped to the requested graticule(s)
    '''

    def __init__(self, target_shape, north=None, south=None, east=None, west=None, **kwargs):
        self.target_shape = target_shape
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        
    def manipulate(self):
        #extract target_shape geometry
        target_shape = self.target_to_valid_geom(self.target_shape)
        
        #construct graticule box
        box_builder = self.GraticuleBoxBuilder(self, target_shape)
        graticule_box = box_builder.build_box()
        
        #intersect the two geometries
        try:
            clipped_shape = target_shape.intersection(graticule_box)
        except Exception, e:
            raise self.InternalException("Exception raised in ClipToGraticuleManipulator while intersecting geometries: " + e.message)

        #if there was no overlap (intersection was empty)
        if clipped_shape.area == 0:
            #message = "clipped geometry is empty (there was no intersection/overlap with the graticules)"
            status_html = render_to_string(self.Options.html_templates["2"], {'MEDIA_URL':settings.MEDIA_URL})
            #return {"message": "clipped geometry is empty (there was no intersection/overlap with the graticules)", "html": status_html, "clipped_shape": clipped_shape, "original_shape": target_shape}
            return self.result(clipped_shape, status_html)
        
        #if there was overlap
        largest_poly = LargestPolyFromMulti(clipped_shape)
        #message = "Graticule clipping was a success"
        status_html = render_to_string(self.Options.html_templates["0"], {'MEDIA_URL':settings.MEDIA_URL})
        #return {"message": "Graticule clipping was a success", "html": status_html, "clipped_shape": largest_poly, "original_shape": target_shape}
        return self.result(largest_poly, status_html)        
    
    class GraticuleBoxBuilder():
        '''
            required argument: 
                target_shape:  GEOSGeometry of the shape to be clipped, in srid GEOMETRY_CLIENT_SRID (4326)
            build_box() return value:
                a box like geometry built from the graticules provided to the manipulator class, completing any 
                missing north, south, east, or west values with the extent of the target shape geometry
                returned shape geometry will be in srid GEOMETRY_CLIENT_SRID (4326) 
        '''
        
        def __init__(self, parent, shape):
            self.__extract_dirs(parent)
            self.__build_extent(shape)
            
        def build_box(self):
            '''
                top_left = (west, north)
                top_right = (east, north)
                bottom_right = (east, south)
                bottom_left = (west, south)
            '''
            try:
                box = Polygon( LinearRing([ Point( float(self.west), float(self.north) ), Point( float(self.east), float(self.north) ), Point( float(self.east), float(self.south) ), Point( float(self.west), float(self.south) ), Point( float(self.west), float(self.north))]))
                box.set_srid(settings.GEOMETRY_CLIENT_SRID)
                return box
            except Exception, e:
                raise self.InternalException("Exception raised in ClipToGraticuleManipulator while initializing graticule geometry: " + e.message)
        
        def __extract_dirs(self, parent):
            self.parent = parent
            self.north = self.parent.north
            self.south = self.parent.south
            self.east = self.parent.east
            self.west = self.parent.west
        
        def __build_extent(self, shape):
            #we will use target_shape.extent to fill in any missing graticule values
            geom_extent = shape.extent
            #fill in any missing graticule params with geom_extent (xmin, ymin, xmax, ymax) values
            if self.north is None:
                self.north = geom_extent[3]
            if self.south is None:
                self.south = geom_extent[1]
            if self.east is None:
                self.east = geom_extent[2]
            if self.west is None:
                self.west = geom_extent[0]
    
    
    class Form(forms.Form):
        available = True
        n = forms.FloatField( label='Northern boundary', required=False ) 
        s = forms.FloatField( label='Southern boundary', required=False )
        e = forms.FloatField( label='Eastern boundary', required=False )
        w = forms.FloatField( label='Western boundary', required=False )
        target_shape = forms.CharField( widget=forms.HiddenInput )
        
        def clean(self):
            data = self.cleaned_data
            
            #the following is used for manipulators testing only
            #data["n"] = 33.75
            #data["e"] = -118.75 
            #data["s"] = 33.25
            #data["w"] = -119.25
            
            my_manipulator = ClipToGraticuleManipulator( data['target_shape'], data['n'], data['s'], data['e'], data['w'] )
            self.manipulation = my_manipulator.manipulate()
            return self.cleaned_data

        
    class Options:
        name = 'ClipToGraticule'
        html_templates = {
            '0':'manipulators/graticule.html', 
            '2':'manipulators/no_graticule_overlap.html',
        }

manipulatorsDict[ClipToGraticuleManipulator.Options.name] = ClipToGraticuleManipulator        


def get_url_for_model(model):
    names = []
    for manipulator in model.Options.manipulators:
        names.append(manipulator.Options.name)
    return reverse('manipulate', args=[','.join(names)])